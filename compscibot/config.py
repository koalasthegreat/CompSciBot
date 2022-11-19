import os

from dotenv import load_dotenv

# load values from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", default="c!")
THRESHOLD = int(os.getenv("THRESHOLD", default=3))
BOT_ROLE = os.getenv("BOT_ROLE", default="bot")
MEMBER_ROLE = os.getenv("MEMBER_ROLE", default="member")
STARBOARD_NAME = os.getenv("STARBOARD_NAME", default="starboard")
AUTOASSIGN_ROLES = bool(os.getenv("AUTOASSIGN_ROLES", default=True))
