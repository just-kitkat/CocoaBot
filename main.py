import os
from vars import *
import discord
from discord.ext import commands

import keep_alive
keep_alive.keep_alive()

intents = discord.Intents.default()
intents.members = True
activity = discord.Game(name=f"Welcome to {bot_name}! | Ping for help!")

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.db = {}

    async def emby(self, ctx, title, description, color):
      embed = discord.Embed(title = title, description = description, color = color)
      await ctx.reply(embed = embed, mention_author = False)
      
bot = MyBot(command_prefix = ",", intents=intents, case_insensitive = True, activity = activity)

bot.help_command = None

for file in os.listdir("./cogs"):
  if file.endswith(".py"):
    try:
      bot.load_extension(f"cogs.{file[:-3]}")
      print(f"Loaded {file} successfully!")
    except Exception as e:
      print(f"Failed to load {file} \nERROR: {e}")


bot.run(os.getenv("TOKEN"))