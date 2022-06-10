import os
from vars import *
import pymongo, dns
from pymongo import MongoClient
import discord
from discord.ext import commands

import keep_alive
keep_alive.keep_alive()

intents = discord.Intents.default()
intents.members = True
activity = discord.Game(name=f"Welcome to {bot_name}! | Ping for help!")

class Help(commands.MinimalHelpCommand):
  async def send_pages(self):
      destination = self.get_destination()
      for page in self.paginator.pages:
          emby = discord.Embed(description=page, color = discord.Color.blurple())
          await destination.send(embed=emby)



class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.db = {}

    # Functions
    async def emby(self, ctx, title, description, color):
      embed = discord.Embed(title = title, description = description, color = color)
      await ctx.reply(embed = embed, mention_author = False)

    # Updates the bot status channel
    async def update_status(self, down = None):
      guild = self.bot.get_guild(936983441516396554)
      status_channel = guild.get_channel(953971108443488286)
      status_msg = await status_channel.fetch_message(955673312602759208)
      if down is None:
        current_time = int(_time.time())
        hour = (current_time - online_since) // 3600
        min = (current_time - online_since) % 3600//60
        sec = (current_time - online_since) % 60
        uptime = f"{hour} hours {min} minutes {sec} seconds"
        title, message, color = f"{bot_name} is online  :green_circle:", f"Last pinged: <t:{int(_time.time())}:R> \nUptime: **{uptime}**", discord.Color.green()
      else:
        title, message, color = f"{bot_name} is offline  :red_circle:", f"Last pinged: <t:{int(_time.time())}:R> \n{bot_name} will be offline for maintenence", discord.Color.red()
      embed = discord.Embed(
        title = title,
        description = message,
        color = color 
      )
      await status_msg.edit(embed = embed)
    
    async def id_from_ping(self, arg):
      if arg[0] == "<":
        return arg[2:-1].replace("!", "")
      else:
        return arg
    
    async def celebrity_appearance(self, user):
      user = str(user)
      rng = random.randint(1, 20)
      if rng == 10:
        rngmoney = random.randint(int(await get_income(user) / 20), await get_income(user) * 2)
        msg = f"**{random.choice(celebrities)}** just showed up and gave you a tip of **{rngmoney} {coin}**"
        bot.db["economy"]["users"][user]["balance"] += rngmoney
      else:
        msg = ""
      return msg
    
    async def log_action(self, ctx, type, message):
      title, color = "Action Log", green
      if type.lower() == "guild":
        channel = self.bot.get_guild(936983441516396554).get_channel(957566232029188096)
        title = "Guild Action"
      else:
        return
      embed = discord.Embed(title = title, description = message, color = color)
      await channel.send(embed = embed)
    
    async def guild_xp(self, ctx, xp):
      user = ctx.author.id
      if bot.db["economy"]["users"][str(user)]["guild"] != "":
        guild_name = bot.db["economy"]["users"][str(user)]["guild"]
        guild_members = len(db["economy"]["guild"][guild_name]["members"])
        guild_level = bot.db["economy"]["guild"][guild_name]["level"]
        guild_xp = bot.db["economy"]["guild"][guild_name]["xp"]
        guild_xpneeded = bot.db["economy"]["guild"][guild_name]["xp_needed"]
        bot.db["economy"]["guild"][guild_name]["xp"] += xp
        
        if bot.db["economy"]["guild"][guild_name]["xp"] >= guild_xpneeded:
          
          bot.db["economy"]["guild"][guild_name]["level"] += 1
          guild_level_up = bot.db["economy"]["guild"][guild_name]["level"]
          bot.db["economy"]["guild"][guild_name]["xp_needed"] = int(50 * 1.2 ** guild_level_up)
          xp_needed_up = bot.db["economy"]["guild"][guild_name]["xp_needed"]
          bot.db["economy"]["guild"][guild_name]["xp"] -= guild_xpneeded
          guild_xp = bot.db["economy"]["guild"][guild_name]["xp"]
          emoji = ""
          xp_emoji = "🟩"
          no_xp_emoji = "⬛"
          levels = int(guild_xp/xp_needed_up * 10)
          for i in range(0, levels):
            emoji += xp_emoji
          for i in range(0, 10 - levels):
            emoji += no_xp_emoji
          embed = discord.Embed(
            title = "Guilds",
            description = f"**{guild_name}** just leveled up! **{guild_level} ⇨ {guild_level_up}** \n{emoji} `({guild_xp} / {xp_needed_up})`",
            color = green
          )
          await ctx.reply(embed = embed, mention_author = False)
    
    async def check_achievements(self, ctx, extra = None):
      user = str(ctx.author.id)
      bal = bot.db["economy"]["users"][user]["balance"]
      stats = bot.db["economy"]["users"][user]["stats"]
    #  for type in ("million", "work", "tip", "clean", "praise", "leaderboard", "manager", "guild"):
    #    if not bot.db["economy"]["users"][user]["achievements"][type]:
      if extra is not None and not bot.db["economy"]["users"][user]["achievements"]["leaderboard"]:
        message = f"**Top of the World!** Your reputation increased by **10 {erep}** for being the top on the leaderboards!"
        bot.db["economy"]["users"][user]["rep"] += 10
        bot.db["economy"]["users"][user]["achievements"]["leaderboard"] = True
      else:
        if stats["work"] >= 100 and not bot.db["economy"]["users"][user]["achievements"]["work"]:
          message = f"**Workaholic!** You have gotten **1,000,000 {coin}** bonus for working so hard!"
          bot.db["economy"]["users"][user]["balance"] += 1000000
          bot.db["economy"]["users"][user]["achievements"]["work"] = True
        elif stats["tip"] >= 100 and not bot.db["economy"]["users"][user]["achievements"]["tip"]:
          message = f"**How Wonderfully Delicious!** You have gotten **5 {erep}** for your amazing dessert!"
          bot.db["economy"]["users"][user]["rep"] += 5
          bot.db["economy"]["users"][user]["achievements"]["tip"] = True
        elif bal >= 1000000 and not bot.db["economy"]["users"][user]["achievements"]["million"]:
          xp_notify, xp = await check_xp(ctx, user, 10)
          message = f"**Millionaire!** You have gained **{xp} xp** for being so rich! {xp_notify}"
          bot.db["economy"]["users"][user]["achievements"]["million"] = True
        elif stats["praise"] >= 100 and not bot.db["economy"]["users"][user]["achievements"]["praise"]:
          message = f"**Encourager!** You have earned **100,000 {coin}** for being so generous with your praises!"
          bot.db["economy"]["users"][user]["balance"] += 100000
          bot.db["economy"]["users"][user]["achievements"]["praise"] = True
        elif stats["clean"] >= 25 and not bot.db["economy"]["users"][user]["achievements"]["clean"]:
          message = f"**What a  Clean Place!** You have earned **25,000 {coin}** for having such a clean shop!"
          bot.db["economy"]["users"][user]["balance"] += 25000
          bot.db["economy"]["users"][user]["achievements"]["clean"] = True
        elif bot.db["economy"]["users"][user]["hire"]["manager"] >= 1 and not bot.db["economy"]["users"][user]["achievements"]["manager"]:
          message = f"**I'm Not The Manager?** You have earned **10,000 {coin}** for finally hiring someone to manage your shop!"
          bot.db["economy"]["users"][user]["balance"] += 10000
          bot.db["economy"]["users"][user]["achievements"]["manager"] = True
        elif bot.db["economy"]["users"][user]["guild"] != "" and not bot.db["economy"]["users"][user]["achievements"]["guild"]:
          message = f"**A Place to Call Home!** Your XP Multiplier has increased by **0.25x!**"
          bot.db["economy"]["users"][user]["levels"]["xp_mult"] += 0.25
          bot.db["economy"]["users"][user]["achievements"]["guild"] = True
      
        else:
          return
      embed = discord.Embed(title = "New Achievement Unlocked", description = message, color = green)
      await ctx.send(f"{ctx.author.mention}", embed = embed)
    
            
    async def get_data(self, type, user):
      if type in ("income", "balance"):
        return "{:,.0f}".format(db["economy"]["users"][str(user)][type])
    
    async def notify_user(self, ctx, user, color, message):
      color = discord.Color.green() if color == "green" else red
        
      user = self.bot.get_user(int(user))
      embed = discord.Embed(
        title = f"New Notification!",
        description = message,
        color = color
      )
      embed.set_footer(text = f"Unsubscribe from all notifications using **{prefix}notify**")
      try:
        await user.send(embed = embed)
      except:
        error_embed = discord.Embed(title = "Something went wrong!", description = f"{cross} Something went wrong while trying to message this user. This user might have their DMs closed or have Second Serving blocked!", color = red)
        await ctx.reply(embed = error_embed)
    
      
    async def check_xp(self, ctx, user, amt : int):
      level = bot.db["economy"]["users"][str(user)]["levels"]["level"]
      xp = bot.db["economy"]["users"][str(user)]["levels"]["xp"]
      xp_mult = bot.db["economy"]["users"][str(user)]["levels"]["xp_mult"]
      guild_name = bot.db["economy"]["users"][str(user)]["guild"]
      if guild_name != "":
        guild_mult = bot.db["economy"]["guild"][guild_name]["xp_mult"]
      else:
        guild_mult = 1
      updated_xp = round(xp + amt * (xp_mult + guild_mult))
      await guild_xp(ctx, round(amt * (xp_mult + guild_mult)))
      xp_needed = bot.db["economy"]["users"][str(user)]["levels"]["xp_needed"]
      xp = updated_xp
      if updated_xp >= xp_needed:
        bot.db["economy"]["users"][str(user)]["levels"]["level"] += 1
        bot.db["economy"]["users"][str(user)]["levels"]["xp"] = 0 + updated_xp - xp_needed
        bot.db["economy"]["users"][str(user)]["levels"]["xp_needed"] = int(10 * 1.2 ** level)
        if level+1 == 2:
          msg = f"\nYou have earned **1000 {coin}**!"
          bot.db["economy"]["users"][str(user)]["balance"] += 1000
        elif level+1 == 5:
          msg = f"\nYou have earned **10,000 {coin}**!"
          bot.db["economy"]["users"][str(user)]["balance"] += 10000
        elif level+1 == 10:
          msg = f"\nYou have unlocked monthly rewards! Use `{prefix}monthly` to claim it!"
        elif level+1 == 20:
          msg = f"\nYou have unlocked **Expeditions**! Use `{prefix}expedition` to get started!"
        elif level+1 == 30:
          msg = f"\nYou have earned **1,000,000 {coin}**!"
          bot.db["economy"]["users"][str(user)]["balance"] += 1000000
        else:
          msg = ""
        return f"\nYou leveled up! You are now level **{level + 1}** {msg} ", round(amt * (xp_mult + guild_mult))
      else:
        bot.db["economy"]["users"][str(user)]["levels"]["xp"] = updated_xp
        return f" `{updated_xp} / {xp_needed}`", round(amt * (xp_mult + guild_mult))
    
    async def get_income(self, user, format = None):
      total = 0
      boost = {}
      user = str(user)
      # Singer
      boost["singer"] = bot.db["economy"]["users"][user]["boost"]["singer"]
      boost["singer_income"] = 1000
    
      # Guitarist
      boost["guitarist"] = bot.db["economy"]["users"][user]["boost"]["guitarist"]
      boost["guitarist_income"] = 10000
    
      # Pianist
      boost["pianist"] = bot.db["economy"]["users"][user]["boost"]["pianist"]
      boost["pianist_income"] = 4000
    
      # Band
      boost["band"] = bot.db["economy"]["users"][user]["boost"]["band"]
      boost["band_income"] = 10000
    
      # Magician
      boost["magician"] = bot.db["economy"]["users"][user]["boost"]["magician"]
      boost["magician_income"] = 8000
      for boosts in bot.db["economy"]["users"][user]["boost"]:
        if bot.db["economy"]["users"][user]["boost"][boosts] > 0:
          total += boost[boosts + "_income"]
      income = bot.db["economy"]["users"][user]["income"]
      total += income
      if format is None:
        return total
      else: 
        return "{:,.0f}".format(total)
    
    # STATS COUNT THINGY
    async def user_stats(self, ctx, type):
      user = str(ctx.author.id)
      if type in ("work", "tip", "clean", "praise", "overtime"):
        bot.db["economy"]["users"][user]["stats"][type] += 1
    
    async def check_blacklists(self):
      for user in list(db["economy"]["user_blacklist"]):
        if bot.db["economy"]["user_blacklist"][user]["time"] <= int(_time.time()):
          bot.db["economy"]["user_blacklist"].pop(user)
          embed = discord.Embed(
            title = bot_name, 
            description = f"You have been unblacklisted. \nPlease note that breaking the rules again will lead to a **harsher** punishment!",
            color = discord.Color.green()
          )
          user = self.bot.get_user(int(user))
          await user.send(embed = embed)

    async def save_db(self):
      collection.replace_one({"_id" : 11}, {"_id" : 11, "economy" : db["economy"]})

    async def login(self, token: str, *, bot: bool = True) -> None:
      await super().login(os.getenv("TOKEN"), bot = bot)
      
      


      print("Setup!") # Task here

      
bot = MyBot(
  command_prefix = ",", 
  intents=intents, 
  case_insensitive = True, 
  activity = activity
)
bot.db = {}
bot.help_command = Help()
mongo_connection_string = os.getenv("mcs")
cluster = pymongo.MongoClient(mongo_connection_string)
database = cluster["SecondServng"]
collection = database["db"]

results = collection.find({"_id" : 11})
for result in results:
  bot.db = result




for file in os.listdir("./cogs"):
  if file.endswith(".py"):
    try:
      bot.load_extension(f"cogs.{file[:-3]}")
      print(f"{tick} Loaded {file}")
    except Exception as e:
      print(f"{cross} Failed to load {file} \nERROR: {e}")


bot.run(os.getenv("TOKEN"))