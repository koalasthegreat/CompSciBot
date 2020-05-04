import os
import re
import dataset
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# load values from .env
load_dotenv()
TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX', default="c!")
THRESHOLD = os.getenv('THRESHOLD', default=3)
BOT_ROLE = os.getenv('BOT_ROLE', default="bot")
MEMBER_ROLE = os.getenv('MEMBER_ROLE', default="member")
STARBOARD_NAME = os.getenv('STARBOARD_NAME', default="starboard")
AUTOASSIGN_ROLES = os.getenv('AUTOASSIGN_ROLES', default=True)

# load database connection
db = dataset.connect('sqlite:///bot.db')
table = db['posts']

# init bot
bot = commands.Bot(command_prefix = PREFIX)

# creates and formats the message to be sent to a starboard
def construct_starboard_message(message):
    author = message.author
    channel = message.channel
    attachments = message.attachments

    title = "**Posted in " + str(channel.name) + ":**"
    link = "\n\n[link to post](" + str(message.jump_url) + ")"

    embed = discord.Embed(type="rich", timestamp=message.created_at)
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    embed.add_field(name=title, value=message.content + link)

    attach_text = ""
    for attachment in attachments:
        attach_text += attachment.url + "\n"
    for url in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content):
        attach_text += url + "\n"
        
    return (attach_text, embed)

# adds a message to the db if it does not already exist, returns true if success, false otherwise
def check_add_message_to_db(message):
    if table.find_one(post_id=message.id) is None:
        data = dict(post_id=message.id, user_id=message.author.id, guild_id=message.guild.id, timestamp=message.created_at)
        try:
            table.insert(data)
            print("Post with id " + str(message.id) + " added to database")
            return True
        except:
            print("ERROR: Could not add post to database")
            return False
    else:
        print("Post with id " + str(message.id) + " already in database")
        return False

# a coroutine to add a message to the starboard channel in a server
async def add_to_starboard(message):
    if message.channel.name != STARBOARD_NAME:
        if (check_add_message_to_db(message)):
            starboard = discord.utils.get(message.guild.text_channels, name=STARBOARD_NAME)

            (attachment_links, embed) = construct_starboard_message(message)

            await starboard.send(embed=embed)
            if (attachment_links != ""):
                await starboard.send("**Attached links:**\n\n" + str(attachment_links))
    else:
        print("Ignoring adding post with id " + str(message.id))


@bot.event
async def on_ready():
    print("Bot is online")

# assigns either a bot role or member role to a user when they join 
@bot.event
async def on_member_join(member):
    try:
        if (member.bot):
            await member.add_roles(
                discord.utils.get(member.guild.roles, name=BOT_ROLE),
                reason="Automatically assigned bot role"
            )
        else:
            await member.add_roles(
                discord.utils.get(member.guild.roles, name=MEMBER_ROLE),
                reason="Automatically assigned user role"
            )
    except:
        print("ERROR: Could not assign a role to " + str(member.name))

# listens for reactions and adds post if it reaches the threshold
@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message

    if (reaction.emoji == "⭐"):
        if (reaction.count == int(THRESHOLD)):
            await add_to_starboard(message)
                
# simple ping command
@bot.command(name='ping',
brief="Responds in the called channel",
description="""
Responds with 'pong' in the channel this command was invoked from
"""
)
async def _ping(ctx):
    await ctx.send('pong')
    print("pong")

# populates the starboard using the pinned messages of all channels
@bot.command(name='populate',
brief="Populates starboard from channel pins",
description="""
Populates the set starboard channel with the pinned 
messages from all other channels

This command is only usable by the server owner
"""
)
@commands.is_owner()
async def _populate(ctx):
    channels = ctx.guild.text_channels

    for channel in channels:
        pins = await channel.pins()

        for pin in pins:
            await add_to_starboard(pin)
            await asyncio.sleep(5)

    print("Population of pins finished")

bot.run(TOKEN)