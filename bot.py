import asyncio
import logging
import os
import re
import sys

import dataset
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.sql import functions, select

# load values from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", default="c!")
THRESHOLD = int(os.getenv("THRESHOLD", default=3))
BOT_ROLE = os.getenv("BOT_ROLE", default="bot")
MEMBER_ROLE = os.getenv("MEMBER_ROLE", default="member")
STARBOARD_NAME = os.getenv("STARBOARD_NAME", default="starboard")
AUTOASSIGN_ROLES = bool(os.getenv("AUTOASSIGN_ROLES", default=True))

# init logger
logging.basicConfig(
    filename="bot.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("CompSciBot")
logger.addHandler(logging.StreamHandler(sys.stdout))

# load database connection
db = dataset.connect("sqlite:///bot.db")
table = db["posts"]

# init bot
bot = commands.Bot(command_prefix=PREFIX)

# creates and formats the message to be sent to a starboard
def construct_starboard_message(message):
    author = message.author
    channel = message.channel
    attachments = message.attachments

    title = "**Posted in " + str(channel.name) + ":**"
    link = "\n\n[link to post](" + str(message.jump_url) + ")"
    field_text = message.content + link
    if len(field_text) >= 1024:
        field_text = message.content[: ((1024 - len(link)) - 10)] + "..." + link

    embed = discord.Embed(type="rich", timestamp=message.created_at)
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    embed.add_field(name=title, value=field_text)

    attach_text = ""
    for attachment in attachments:
        attach_text += attachment.url + "\n"
    for url in re.findall(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        message.content,
    ):
        attach_text += url + "\n"

    if len(attach_text) > 2000:
        attach_text = attach_text[:1990] + "..."

    return (attach_text, embed)


# adds a message to the db if it does not already exist, returns true if success, false otherwise
def check_add_message_to_db(message):
    if table.find_one(post_id=message.id) is None:
        data = dict(
            post_id=message.id,
            user_id=message.author.id,
            guild_id=message.guild.id,
            timestamp=message.created_at,
        )
        try:
            table.insert(data)
            logger.info(f"Post with id {message.id} added to database")
            return True
        except:
            logger.warning(f"Could not add post with id {message.id} to database")
            return False
    else:
        logger.info(f"Post with id {message.id} already in database")
        return False


# a coroutine to add a message to the starboard channel in a server
async def add_to_starboard(message):
    if message.channel.name != STARBOARD_NAME:
        if check_add_message_to_db(message):
            starboard = discord.utils.get(
                message.guild.text_channels, name=STARBOARD_NAME
            )

            (attachment_links, embed) = construct_starboard_message(message)

            await starboard.send(embed=embed)
            if attachment_links != "":
                await starboard.send("**Attached links:**\n\n" + str(attachment_links))
    else:
        logger.info(f"Ignoring adding post with id {message.id}")


@bot.event
async def on_ready():
    logger.info("Bot is online")


# assigns either a bot role or member role to a user when they join
@bot.event
async def on_member_join(member):
    if AUTOASSIGN_ROLES:
        try:
            if member.bot:
                await member.add_roles(
                    discord.utils.get(member.guild.roles, name=BOT_ROLE),
                    reason="Automatically assigned bot role",
                )
                logger.info(f"Added bot role {BOT_ROLE} to {member.name}")
            else:
                await member.add_roles(
                    discord.utils.get(member.guild.roles, name=MEMBER_ROLE),
                    reason="Automatically assigned user role",
                )
                logger.info(f"Added user role {MEMBER_ROLE} to {member.name}")
        except:
            logger.warning(f"Could not assign a role to {member.name}")


# listens for reactions and adds post if it reaches the threshold
@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message

    if reaction.emoji == "⭐":
        logger.info(
            f"User with name {user.name} and id {user.id} reacted to {message.id}"
        )

        if reaction.count >= THRESHOLD:
            count = 0
            users = await reaction.users().flatten()
            for user in users:
                if not user.bot:
                    count += 1

            if count >= THRESHOLD:
                await add_to_starboard(message)


# simple ping command
@bot.command(
    name="ping",
    brief="Responds in the called channel",
    description="""
Responds with 'pong' in the channel this command was invoked from
""",
)
async def _ping(ctx):
    await ctx.send("pong")
    logger.info("pong")


# populates the starboard using the pinned messages of all channels
@bot.command(
    name="populate",
    brief="Populates starboard from channel pins",
    description="""
Populates the set starboard channel with the pinned 
messages from all other channels

This command is only usable by the server owner
""",
)
@commands.is_owner()
async def _populate(ctx):
    channels = ctx.guild.text_channels

    all_pins = []

    for channel in channels:
        pins = await channel.pins()

        for pin in pins:
            all_pins.append(pin)

    all_pins.sort(key=lambda x: x.created_at)

    for pin in all_pins:
        await add_to_starboard(pin)
        await asyncio.sleep(5)

    logger.info("Population of pins finished")


@bot.command()
async def randompost(ctx: commands.Context):
    """Get a random post from the starboard."""
    posts_table = table.table
    post = next(
        db.query(
            posts_table.select().where(
                posts_table.c.id.in_(
                    select(posts_table.c.id).order_by(functions.random()).limit(1)
                )
            )
        )
    )

    for channel in ctx.guild.channels:
        if not isinstance(channel, discord.TextChannel):
            continue
        try:
            message = await channel.fetch_message(post["post_id"])
            break
        except (discord.NotFound, discord.Forbidden):
            continue
    else:
        ctx.reply(":frowning_face: Seems the message I grabbed couldn't be found.")
        return

    (attachment_links, embed) = construct_starboard_message(message)

    await ctx.send(embed=embed)
    if attachment_links != "":
        await ctx.send("**Attached links:**\n\n" + str(attachment_links))


bot.run(TOKEN)
