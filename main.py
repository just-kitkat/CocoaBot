import os
import asyncio
import time
import random
import math
from vars import *
from errors import *
import pymongo
import dns
from pymongo import MongoClient
import discord
from discord import app_commands
from discord.ext import commands, tasks


import keep_alive
keep_alive.keep_alive()

import logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
activity = discord.Game(name=f"This is {bot_name}! | Type / to get started!")

stop_bot = os.environ["STOP_BOT"]



class MyBot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  async def interaction_check(self, itx: discord.Interaction) -> bool:
    return False

  # Functions 
  async def save_db(self):
    try:
      collection.replace_one({"_id" : 63}, {"_id" : 63, "economy" : bot.db["economy"]})
      collection.replace_one({"_id" : 64}, {"_id" : 64, "others" : bot.dbo["others"]})
    except Exception as e:
      log_channel = bot.get_channel(1030104234278014976)
      #print(bot.db, bot.dbo)
      embed = discord.Embed(title="DB Error", description=f"{e}")
      await log_channel.send(embed=embed)
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

  async def check_xp(self, user, amt : int) -> str:
    """
    Add + check xp of a user and return a xp msg
    """
    # REMEMBER TO ADD GUILD MULT
    level = bot.db["economy"][str(user)]["levels"]["level"]
    xp = bot.db["economy"][str(user)]["levels"]["xp"]
    xp_mult = bot.db["economy"][str(user)]["levels"]["xp_mult"]
    personal_mult = 0
    boosts = bot.db["economy"][str(user)]["boosts"]
    type_ = "xp"
    for boost in range(len(boosts[type_])): # boost = {mult: duration}
      for k in boosts[type_][boost]:
        personal_mult += float(k)
    total_mult = round(amt * (xp_mult + personal_mult))
    updated_xp = round(xp + total_mult) # + guild mult
    print(xp, xp_mult, personal_mult, total_mult, updated_xp, user)
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
      print("test 1", bot.db["economy"][str(user)]["levels"]["xp"])
      bot.db["economy"][str(user)]["levels"]["xp"] = updated_xp
      print("test 2", bot.db["economy"][str(user)]["levels"]["xp"])
      return f"\nXp Earned: **{total_mult} 🔹** `{updated_xp} / {xp_needed}`"

  async def get_income(self, userid):
    """
    Gets user's income based on upgrades and boosters
    """
    userid = str(userid)
    income = bot.db["economy"][userid]["income"]
    income_boost = bot.db["economy"][userid]["income_boost"]
    if bot.dbo["others"]["global_income_boost"] != {}:
      global_boost = float(list(bot.dbo["others"]["global_income_boost"].keys())[0])
    else:
      global_boost = 0
    personal_mult = 0
    boosts = bot.db["economy"][userid]["boosts"]
    type_ = "income"
    for user in bot.db["economy"]:
      for boost in range(len(boosts[type_])): # boost = {mult: duration}
        for k in boosts[type_][boost]:
          personal_mult += float(k)
    income = income * (income_boost + global_boost + personal_mult)
    return income, (income_boost, global_boost, personal_mult)
  
  #async def setup_hook(self):


class MyTree(app_commands.CommandTree):
  async def interaction_check(self, itx: discord.Interaction) -> bool:
    """
    Checks for blacklisted users, maintenance mode and alerts
    """
    blacklist = itx.client.dbo["others"]["user_blacklist"]
    if str(itx.user.id) in blacklist:
      if int(time.time()) < blacklist[str(itx.user.id)]["time"]:
        duration = blacklist[str(itx.user.id)]["time"]
        reason = blacklist[str(itx.user.id)]["reason"]
        await itx.response.send_message(f"""
You are currently blacklisted! 
Reason: {reason}
Blacklist ends <t:{duration}:R>
Dm me `.info` to join the support server!"""
  )
        return False
      else:
        itx.client.dbo["others"]["user_blacklist"].pop(str(itx.user.id))
      
    
    itx.client.dbo["others"]["total_commands_ran"] += 1
    if itx.client.dbo["others"]["maintenancemode"] and itx.user.id != 915156033192734760:
      await itx.response.send_message("I am currently on maintenance mode! Join my support server for more info. \nDm me `.info` to join the support server!")
      return False
    if itx.user.id not in itx.client.dbo["others"]["read_alert"] and itx.client.dbo["others"]["alert_ping"]:
      await itx.channel.send(f"{itx.user.mention}, there is an important alert! \nUse `{prefix}alert` to view it!")

    # cleanliness warning
    if str(itx.user.id) in itx.client.db["economy"] and itx.client.db["economy"][str(itx.user.id)]["cleanliness"] <= 25:
      await itx.channel.send(f"{itx.user.mention}, you have not cleaned your farm for a long time... This impacts your hourly income! \nUse `{prefix}clean` to clean your farm!")
    return True

      
bot = MyBot(
  command_prefix = commands.when_mentioned_or("."), 
  intents=intents, 
  case_insensitive = True, 
  activity = activity,
  strip_after_prefix = True,
  tree_cls = MyTree
)
bot.db, bot.dbo = {}, {}
bot.cache = {
  "fishing_cooldown" : {"users" : {}},
  "uptime": int(time.time()),
  "logged_restart": False
}
bot.prefix = "/"
bot.giving_income = False


# MC Connection
mcs = os.getenv("mcs")
cluster = pymongo.MongoClient(mcs)
database = cluster["CocoaBot"]
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