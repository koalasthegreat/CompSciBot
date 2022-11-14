import asyncio

import discord
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.sql import functions

from compscibot.bot import bot, logger
from compscibot.db import async_session
from compscibot.models import Post
from compscibot.utils.starboard import add_to_starboard, construct_starboard_message


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
    async with async_session() as session:
        result = await session.execute(select(Post).order_by(functions.random()))
        post = result.scalars().first()

    for channel in ctx.guild.channels:
        if not isinstance(channel, discord.TextChannel):
            continue
        try:
            message = await channel.fetch_message(post.post_id)
            break
        except (discord.NotFound, discord.Forbidden):
            continue
    else:
        await ctx.reply(
            ":frowning: Seems the message I grabbed couldn't be found."
        )
        return

    (attachment_links, embed) = construct_starboard_message(message)

    await ctx.send(embed=embed)
    if attachment_links != "":
        await ctx.send("**Attached links:**\n\n" + str(attachment_links))
