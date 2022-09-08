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

  async def itx_check(self, itx: discord.Interaction, msg: str=None, failed: bool = True):
    if failed:
      if msg is None:
        msg = f"{cross} This is not your button!"
      await itx.response.send_message(f"{msg}", ephemeral = True)
      return False
    return True

  async def check_quests(self, itx: discord.Interaction) -> str:
    quest = bot.db["economy"][str(itx.user.id)]["quest"]
    last_quest = bot.db["economy"][str(itx.user.id)]["last_quest"]
    
    if last_quest + 86400 <= int(time.time()):
      # Fish Quest Gen
      fish_luck = random.randint(1, 10)
      if fish_luck < 4: fish = "tuna"
      if 4 <= fish_luck < 6: fish = "grouper"
      if 6 <= fish_luck < 8: fish = "snapper"
      if 8 <= fish_luck < 10: fish = "salmon"
      if fish_luck >= 10: fish = "cod"
        
      if fish == "tuna": 
        fish_times = random.randint(5, 50)
      elif fish == "cod":
        fish_times = random.randint(1,5)
      else:
        fish_times = random.randint(6, 30)
      fish_completed = False
      bot.db["economy"][str(itx.user.id)]["quest"]["fish"] = {
        "name" : fish, "times" : fish_times, "completed" : fish_completed
      }

      # Hunt Quest Gen
      pet_level = bot.db["economy"][str(itx.user.id)]["pets"]["level"]
      hunt_times = random.randint(pet_level - 2, pet_level + 2)
      hunt_times = random.randint(2,5) if hunt_times < 3 else hunt_times
      hunt_completed = False
      hunt_times_completed = 0
      bot.db["economy"][str(itx.user.id)]["quest"]["hunt"] = {
        "times" : hunt_times, "completed" : hunt_completed, "times_completed": hunt_times_completed
      }
      
      bot.db["economy"][str(itx.user.id)]["last_quest"] = int(time.time())
    else:
      fish_times = quest["fish"]["times"]
      fish = quest["fish"]["name"]
      fish_completed = quest["fish"]["completed"]
      hunt_times = quest["hunt"]["times"]
      hunt_times_completed = quest["hunt"]["times_completed"]
      hunt_completed = quest["hunt"]["completed"]
    hunt_progress = f"`({hunt_times_completed} / {hunt_times})`" if not hunt_completed else ""
    fish_progress = f'`({bot.db["economy"][str(itx.user.id)]["fish"][fish]} / {fish_times})`' if not fish_completed else ""
    fish_msg = f"{tick if fish_completed else cross} Submit **{fish_times} {fish}s** {fish_progress}"
    hunt_msg = f"{tick if hunt_times_completed >= hunt_times else cross} Go out hunting **{hunt_times} times.** {hunt_progress}"
    return fish_msg, hunt_msg

  
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
bot.cache = {
  "fishing_cooldown" : {"users" : {}}
}
bot.prefix = "/"
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
  print("after_invoked called")
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