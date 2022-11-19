import logging
import sys

import discord
from discord.ext import commands

from compscibot import config

logging.basicConfig(
    filename="bot.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("CompSciBot")
logger.addHandler(logging.StreamHandler(sys.stdout))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)
