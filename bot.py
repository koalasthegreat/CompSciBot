import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# load token from .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

# init bot
bot = commands.Bot(command_prefix = "c!")

@bot.event
async def on_ready():
    print("Bot is online.")

@bot.event
async def on_member_join(member):
    if (member.bot):
        await member.add_roles(
            discord.utils.get(member.guild.roles, name="bot"),
            reason="Automatically assigned bot role."
        )
    else:
        await member.add_roles(
            discord.utils.get(member.guild.roles, name="CompSci Boi"),
            reason="Automatically assigned user role."
        )


@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(TOKEN)