import os, asyncio, time, random
#os.system("pip install git+https://github.com/Rapptz/discord.py")
from vars import *
import pymongo, dns
from pymongo import MongoClient
import discord
from discord.ext import commands, tasks

import keep_alive
keep_alive.keep_alive()

import logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
activity = discord.Game(name=f"This is {bot_name} Beta! | Ping for help!")



class MyBot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  # Functions 
  async def save_db(self):
    collection.replace_one({"_id" : 63}, {"_id" : 63, "economy" : bot.db["economy"]})
    collection.replace_one({"_id" : 64}, {"_id" : 64, "others" : bot.dbo["others"]})

  
# async def setup_hook(self):

def get_prefix(bot, message):
  id = message.guild.id
  if str(id) in bot.db["economy"]["prefix"]:
    bot.prefix = bot.db["economy"]["prefix"][str(id)]
  else:
    bot.prefix = ","
  prefixes = [bot.prefix.lower(), bot.prefix.upper()]
  return commands.when_mentioned_or(*prefixes) (bot, message)
      
bot = MyBot(
  command_prefix = ".", 
  intents=intents, 
  case_insensitive = True, 
  activity = activity,
  strip_after_prefix = True
)
bot.db, bot.dbo = {}, {}
bot.prefix = "."
bot.giving_income = False


# MC Connection
mcs = os.getenv("mcs")
cluster = pymongo.MongoClient(mcs)
database = cluster["KitkatBot"]
collection = database["db"]

results = collection.find({"_id" : 63})
for result in results:
  bot.db = result
results = collection.find({"_id" : 64})
for result in results:
  bot.dbo = result


@bot.after_invoke
async def after_invoke(ctx):
  await bot.save_db()

async def main():
  async with bot:
    for file in os.listdir("./cogs"):
      if file.endswith(".py"):
        try:
          await bot.load_extension(f"cogs.{file[:-3]}")
          print(f"{tick} Loaded {file}")
        except Exception as e:
          print(f"{cross} Failed to load {file} \nERROR: {e}")
    await bot.start(os.getenv("TOKEN"))

if __name__ == "__main__":
  asyncio.run(main())