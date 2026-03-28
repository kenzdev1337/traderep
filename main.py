import discord
import os
import asyncio

from dotenv import load_dotenv
from discord.ext.commands import Bot

bot = Bot(command_prefix=os.getenv("BOT_PREFIX_DEPRECIATED"), intents=discord.Intents.all())

load_dotenv()

for file in os.listdir(os.getenv("MODULES_PATH")):
    if file.endswith(".py"):
        asyncio.run(bot.load_extension(f'modules.{file[:-3]}'))
        print(f"Loading module {file[:-3]}")

@bot.event
async def on_ready():
    print("Bot started")

bot.run(os.getenv("TOKEN"))