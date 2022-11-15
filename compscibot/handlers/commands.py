import asyncio

import discord
from discord.ext import commands
from sqlalchemy import select, update
from sqlalchemy.sql import functions

from compscibot.bot import bot, logger
from compscibot.db import async_session
from compscibot.models import Post
from compscibot.utils.starboard import (
    add_to_starboard,
    construct_starboard_message,
    find_post,
    get_reaction_count,
)


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
@commands.is_owner()
async def filldata(ctx):
    """Populate the data for starboard posts with data from Discord"""
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Post).filter(Post.content == None).order_by(Post.timestamp.asc()))
            posts = result.scalars().all()

            for post in posts:
                message = await find_post(post, ctx)
                if message is None:
                    logger.info(
                        f"Unable to populate message {post.post_id} - message could not be found"
                    )
                    continue

                content = message.content
                channel_id = message.channel.id

                reactions_obj = next((r for r in message.reactions if r.emoji == "⭐"), None)
                star_count = await get_reaction_count(reactions_obj) if reactions_obj is not None else 0

                async with session.begin_nested():
                    await session.execute(
                        update(Post)
                        .where(Post.id == post.id)
                        .values(
                            content=content,
                            channel_id=channel_id,
                            star_count=star_count,
                        )
                    )

                logger.info(f"Populated data for post {post.id}")
            await session.commit()



@bot.command()
async def randompost(ctx: commands.Context):
    """Get a random post from the starboard."""
    async with async_session() as session:
        result = await session.execute(select(Post).order_by(functions.random()))
        post = result.scalars().first()

    message = await find_post(post, ctx)

    if message is None:
        await ctx.reply(":frowning: Seems the message I grabbed couldn't be found.")
        return

    (attachment_links, embed) = construct_starboard_message(message)

    await ctx.send(embed=embed)
    if attachment_links != "":
        await ctx.send("**Attached links:**\n\n" + str(attachment_links))
