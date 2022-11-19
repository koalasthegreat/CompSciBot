import discord

from compscibot import config
from compscibot.bot import bot, logger
from compscibot.models import Post
from compscibot.utils.starboard import add_to_starboard, get_reaction_count


@bot.event
async def on_ready():
    logger.info("Bot is online")


# assigns either a bot role or member role to a user when they join
@bot.event
async def on_member_join(member):
    if config.AUTOASSIGN_ROLES:
        try:
            if member.bot:
                await member.add_roles(
                    discord.utils.get(member.guild.roles, name=config.BOT_ROLE),
                    reason="Automatically assigned bot role",
                )
                logger.info(f"Added bot role {config.BOT_ROLE} to {member.name}")
            else:
                await member.add_roles(
                    discord.utils.get(member.guild.roles, name=config.MEMBER_ROLE),
                    reason="Automatically assigned user role",
                )
                logger.info(f"Added user role {config.MEMBER_ROLE} to {member.name}")
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

        count = await get_reaction_count(reaction)
        await Post.update_star_count(message.id, count)

        if count >= config.THRESHOLD:
            await add_to_starboard(message, count)
