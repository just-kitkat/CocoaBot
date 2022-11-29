import os
import asyncio
import time
import random
import math
from vars import *
import pymongo
import dns
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

stop_bot = os.environ["STOP_BOT"]



class MyBot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  # Functions 
  async def save_db(self):
    try:
      collection.replace_one({"_id" : 63}, {"_id" : 63, "economy" : bot.db["economy"]})
      collection.replace_one({"_id" : 64}, {"_id" : 64, "others" : bot.dbo["others"]})
    except Exception as e:
      log_channel = bot.get_channel(1030104234278014976)
      embed = discord.Embed(title="DB Error", description=e)
      await channel.send(embed=embed)
      exec(stop_bot)

  async def itx_check(self, itx: discord.Interaction, msg: str=None, failed: bool = True):
    if failed:
      if msg is None:
        msg = f"{cross} This is not your button!"
      await itx.response.send_message(f"{msg}", ephemeral = True)
      return False
    return True

  async def check_quests(self, itx: discord.Interaction) -> str:
    quest = bot.db["economy"][str(itx.user.id)]["quest"]
    new_q = False # is a new quest being generated?
    last_quest = bot.db["economy"][str(itx.user.id)]["last_quest"]
    
    if last_quest + 86400 <= int(time.time()):
      new_q = True
      
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
      hunt_times = random.randint(pet_level, pet_level + 3)
      hunt_times = random.randint(2,5) if hunt_times < 3 else hunt_times
      hunt_times_completed = 0
      hunt_completed = False
      bot.db["economy"][str(itx.user.id)]["quest"]["hunt"] = {
        "times" : hunt_times, "completed" : False, "times_completed": 0
      }

      # Income Quest Gen (work x times for now)
      work_times = random.randint(5, 15)
      work_times_completed = 0
      work_completed = False
      bot.db["economy"][str(itx.user.id)]["quest"]["income"] = {
        "times" : work_times, "completed" : False, "times_completed": 0
      }
      
      bot.db["economy"][str(itx.user.id)]["last_quest"] = int(time.time())
    else:
      fish_times = quest["fish"]["times"]
      fish = quest["fish"]["name"]
      fish_completed = quest["fish"]["completed"]
      hunt_times = quest["hunt"]["times"]
      hunt_times_completed = quest["hunt"]["times_completed"]
      hunt_completed = quest["hunt"]["completed"]
      work_times = quest["income"]["times"]
      work_times_completed = quest["income"]["times_completed"]
      work_completed = quest["income"]["completed"]
    hunt_progress = f"`({hunt_times_completed} / {hunt_times})`" if not hunt_completed else ""
    work_progress = f"`({work_times_completed} / {work_times})`" if not work_completed else ""
    fish_progress = f'`({bot.db["economy"][str(itx.user.id)]["fish"][fish]} / {fish_times})`' if not fish_completed else ""
    fish_msg = f"{tick if fish_completed else cross} Submit **{fish_times} {fish}s** {fish_progress}"
    hunt_msg = f"{tick if hunt_times_completed >= hunt_times else cross} Go out hunting **{hunt_times} times.** {hunt_progress}"
    income_msg = f"{tick if work_times_completed >= work_times else cross} Work **{work_times} times.** {work_progress}"
    return new_q, fish_msg, hunt_msg, income_msg

  def get_happiness(self, itx: discord.Interaction):
    """
    Gets a pet's happiness based on it's hunger and boredom levels
    """
    itx.client.db["economy"][str(itx.user.id)]["pets"]["hunger"] = (int(time.time()) - itx.client.db["economy"][str(itx.user.id)]["pets"]["last_feed"])//7200
    itx.client.db["economy"][str(itx.user.id)]["pets"]["boredom"] = (int(time.time()) - itx.client.db["economy"][str(itx.user.id)]["pets"]["last_play"])//7200
    hunger = itx.client.db["economy"][str(itx.user.id)]["pets"]["hunger"]
    boredom = itx.client.db["economy"][str(itx.user.id)]["pets"]["boredom"]
    if hunger > 50: hunger = 50
    if boredom > 50: boredom = 50
    print(boredom, hunger)
    total = 100 - hunger - boredom
    return abs(total)

  async def check_xp(self, user, amt : int):
    """
    Add + check xp of a user and return a xp msg
    """
    # REMEMBER TO ADD GUILD MULT
    level = bot.db["economy"][str(user)]["levels"]["level"]
    xp = bot.db["economy"][str(user)]["levels"]["xp"]
    xp_mult = bot.db["economy"][str(user)]["levels"]["xp_mult"]
    updated_xp = round(xp + amt * (xp_mult)) # + guild mult
    #await bot.guild_xp(ctx, round(amt * (xp_mult + guild_mult)))
    xp_needed = math.floor(xp_needed_base*1.5*(level**1.2))
    xp = updated_xp
    if updated_xp >= xp_needed:
      bot.db["economy"][str(user)]["levels"]["level"] += 1
      bot.db["economy"][str(user)]["levels"]["xp"] = 0 + updated_xp - xp_needed
      level += 1
      if level == 2:
        msg = f"\nYou have earned **500 {coin}**!"
        bot.db["economy"][str(user)]["balance"] += 1000
      elif level == 5:
        msg = f"\nYou have unlocked the `{prefix}daily` command!"
      elif level == 10:
        msg = f"\nYou have unlocked guilds! To join a guild, use `{prefix}guild join <name>` \n**NOTE: Guilds are a work in progress and have not been added yet.**"
      elif level == 15:
        msg = f"\nYou have unlocked **expeditions**! Use `{prefix}expedition help` for more info. \n**NOTE: Expeditions are a work in progress and have not been added yet.**"
      elif level == 20:
        msg = f"\nYou have unlocked the `{prefix}weekly` command!"
      elif level == 30:
        msg = f"\nYou have unlocked the `{prefix}monthly` command!"
      else:
        reward = level*500
        bot.db["economy"][str(user)]["balance"] += reward
        msg = f"You have earned **{reward} {coin}**!"
      return f"\nYou leveled up! You are now level **{level}** \n{msg}"
    else:
      bot.db["economy"][str(user)]["levels"]["xp"] = updated_xp
      return f"\nXp Earned: **{round(amt * (xp_mult))} 🔹** `{updated_xp} / {xp_needed}`"

  async def get_income(self, userid):
    """
    Gets user's income based on upgrades and boosters
    """
    income = bot.db["economy"][str(userid)]["income"]
    xp_mult = bot.db["economy"][str(userid)]["levels"]["xp_mult"]
    global_boost = 0 # 0 = no global boost
    income = income * (xp_mult + global_boost)
    return income
  
  #async def setup_hook(self):
    

      
bot = MyBot(
  command_prefix = commands.when_mentioned_or("."), 
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
#create a conection to mongodb cluster 
try:
  for result in results:
    bot.db = result
  results = collection.find({"_id" : 64})
  for result in results:
    bot.dbo = result
except:
  print("Could not connect to db, stopping code...")
  exec(stop_bot)


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
  try:
    asyncio.run(main())
  except Exception as e:
    print("Bot ran into error:", e)
    print("You are ratelimited! Stopping code...")
    exec(stop_bot)