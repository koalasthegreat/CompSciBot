import re

import discord

from compscibot import config
from compscibot.bot import logger
from compscibot.models import Post


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
    embed.set_author(name=author.name, icon_url=author.display_avatar.url)
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
async def check_add_message_to_db(message):
    if await Post.get_by_post(post_id=message.id) is None:
        try:
            await Post.add(
                post_id=message.id,
                user_id=message.author.id,
                guild_id=message.guild.id,
                timestamp=message.created_at,
            )
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
    if message.channel.name != config.STARBOARD_NAME:
        if await check_add_message_to_db(message):
            starboard = discord.utils.get(
                message.guild.text_channels, name=config.STARBOARD_NAME
            )

            (attachment_links, embed) = construct_starboard_message(message)

            await starboard.send(embed=embed)
            if attachment_links != "":
                await starboard.send("**Attached links:**\n\n" + str(attachment_links))
    else:
        logger.info(f"Ignoring adding post with id {message.id}")