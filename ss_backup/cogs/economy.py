import discord, time, random, math, asyncio
from vars import *
from datetime import timedelta, date, datetime
from discord.ext import commands

class Economy(commands.Cog, name = "General Commands"):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def build(self, ctx):
    if str(ctx.author.id) not in self.bot.db["economy"]["users"]:
      self.bot.db["economy"]["users"][str(ctx.author.id)] = {
"balance" : 1000, "income" : 500, "tips" : 200, "account_created" : int(time.time()), "happiness" : 100, "daily_streak" : 0, "rush_hour" : 0, "guild" : "", "rep" : 0.00, "rep_cooldowns" : {}, #{user_id : time}
"stats" : {"work" : 0, "tip" : 0, "clean" : 0, "praise" : 0, "overtime" : 0},
"achievements" : {"work" : False, "tip" : False, "clean" : False, "million" : False, "praise" : False, "manager" : False, "leaderboard" : False, "guild" : False}, 
"levels" : {"xp" : 0, "xp_mult" : 1, "level" : 1, "xp_needed" : 20}, 
"cooldowns" : {"work" : 1, "tip" : 1, "clean" : 1, "daily" : 1, "weekly" : 1, "monthly" : 1}, 
"hire" : {"waiter" : 0, "chef" : 1, "head_chef" : 0, "cashier" : 0, "manager" : 0, "cleaner" : 0}, 
"upgrade" : {"tipjar" : 0, "sign" : 0, "paint" : 0, "fan" : 1, "aircon" : 0, "light" : 0}, 
"boost" : {"band" : 0, "pianist" : 0, "guitarist" : 0, "singer" : 0, "magician" : 0}
      }
      embed = discord.Embed(
        title = bot_name,
        description = f"{tick} You have successfully built a dessert shop! \nCheck your DMs for a quick guide! \n`View the tutorial using {self.bot.prefix}tutorial`",
        color = discord.Color.green()
      )
      dm_embed = discord.Embed(
        title = f"{cake} Your brand new **Dessert Shop** is now in business! {cake}",
        description = f"""
You are the owner of your dessert shop and will recieve a hourly income to pay for things!
  
➼ You can increase your income by purchasing **Upgrades**, hiring **Employees**, purchasing **Advertisment** and much more!
➼ You can also **work** and collect **tips** for extra income! (Work: `{self.bot.prefix}work`, Collect tips: `{self.bot.prefix}tips`)
➼ Make sure to **clean** your shop once every 6 hours to keep your customers happy to maximise income!
➼ Become the most successful shop and climb up the leaderboards!
  
To join the **Support Server**, you can click the link below!
Benefits of joining the server:
➼ Participate in lotteries and giveaways.
➼ Make friends and be part of the community!
➼ Get help and updates regarding the development of the bot!
  
**To get started, you can use the `{self.bot.prefix}tutorial` command! Good luck!**
""",
  color = discord.Color.green()
      )
      user = self.bot.get_user(ctx.author.id)
      try:
        await user.send(embed = dm_embed)
        await user.send(f"Join the support server here: {sinvite}")
      except:
        error_embed = discord.Embed(title = "Something went wrong!", description = f"{cross} Something went wrong while trying to message you. You might have your DMs closed or have Second Serving blocked! To view the tutorial, use `{self.bot.prefix}tutorial`", color = red)
        await ctx.reply(embed = error_embed)
    else:
      embed = discord.Embed(
        title = bot_name,
        description = f"{cross} You already own a dessert shop!",
        color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)

  
  @commands.command(aliases = ["w"])
  async def work(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      cooldown = 600
      last_work = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["work"]
      income = self.bot.db["economy"]["users"][str(ctx.author.id)]["income"]
      if int(time.time()) - last_work > cooldown:
        earn = random.randint(income - 200, income + 200)
        self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] += earn
        self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["work"] = int(time.time())
        balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
        happiness = self.bot.db["economy"]["users"][str(ctx.author.id)]["happiness"]
        if happiness < 25:
          notify = f"\nYour customers' happiness is at **{happiness}%**. This will affect your income significantly! Please clean your shop using `{self.bot.prefix}clean`"
        else:
          notify = ""
        xp = random.randint(1,3)
        xp_notify,xp = await self.bot.check_xp(ctx, ctx.author.id, xp)
        celeb_app = await self.bot.celebrity_appearance(str(ctx.author.id))
        embed = discord.Embed(
          title =  bot_name,
          description = f"{tick} You worked in your dessert shop and earned **{earn} {coin}** \nBalance: **{balance} {coin}** \nXP Earned: **{xp} xp** {xp_notify} {notify} \n{celeb_app}",
          color = discord.Color.green()
          )
        await self.bot.user_stats(ctx, "work")
      else:
        last = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["work"]
        currenttime = int(time.time())
        min = str(math.floor((10 - ((currenttime - last) % 3600) / 60)))
        sec = str(math.floor((60 - ((currenttime - last) % 3600) % 60)))
        cooldown = f"{min} minutes {sec} seconds"
        embed = discord.Embed(
          title =  bot_name,
          description = f"{cross} You cannot work so soon! Please wait another `{cooldown}`",
          color = discord.Color.red()
          )
    else:
      embed = discord.Embed(
       title =  bot_name,
       description = f"{cross} You do not own a dessert shop. Do `{self.bot.prefix}build` to build one!",
       color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)

  @commands.command(aliases = ["t", "tips"])
  async def tip(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      cooldown = 300
      last_tip = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["tip"]
      tip = self.bot.db["economy"]["users"][str(ctx.author.id)]["tips"]
      if int(time.time()) - last_tip > cooldown:
        earn = random.randint(tip, tip * 5)
        self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] += earn
        self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["tip"] = int(time.time())
        balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
        xp = random.randint(1,2)
        xp_notify, xp = await self.bot.check_xp(ctx, ctx.author.id, xp)
        celeb_app = await self.bot.celebrity_appearance(str(ctx.author.id))
        await self.bot.user_stats(ctx, "tip")
        embed = discord.Embed(
          title =  bot_name,
          description = f"{tick} You checked your tip jar and found **{earn} {coin}** \nBalance: **{balance} {coin}** \nXP earned: **{xp} xp** \n{xp_notify} \n{celeb_app}",
          color = discord.Color.green()
          )
      else:
        last = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["tip"]
        currenttime = int(time.time())
        min = str(math.floor((5 - ((currenttime - last) % 3600) / 60)))
        sec = str(math.floor((60 - ((currenttime - last) % 3600) % 60)))
        cooldown = f"{min} minutes {sec} seconds"
        embed = discord.Embed(
          title =  bot_name,
          description = f"{cross} It is rude to check your tip jar so often! Try again in `{cooldown}`",
          color = discord.Color.red()
          )
    else:
      embed = discord.Embed(
       title =  bot_name,
       description = f"{cross} You do not own a dessert shop. Do `{self.bot.prefix}build` to build one!",
       color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)                                          

  # Clean Command
  @commands.command()
  async def clean(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      last_clean = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["clean"]
      balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
      income = self.bot.db["economy"]["users"][str(ctx.author.id)]["income"]
      cleaners = self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["cleaner"]
      cooldown = 21600 # 6 hours
      currenttime = int(time.time())
      if currenttime - last_clean > cooldown and cleaners > 0:
        self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] -= income
        self.bot.db["economy"]["users"][str(ctx.author.id)]["happiness"] = 100
        if self.bot.db["economy"]["users"][str(ctx.author.id)]["happiness"] > 100:
          self.bot.db["economy"]["users"][str(ctx.author.id)]["happiness"] = 100
  
        self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["clean"] = int(time.time())
        balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
        if balance < 0:
          self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] = 0
          balance = 0
        await self.bot.user_stats(ctx, "clean")
        embed = discord.Embed(
          title =  bot_name,
          description = f"{tick} You paid your cleaners **{income} {coin}** and your customers' happiness increased by **50%**! \nBalance: **{balance} {coin}**",
          color = discord.Color.green()
          )
      elif cleaners < 1:
        embed = discord.Embed(
          title =  bot_name,
          description = f"{cross} You did not employ any cleaners! Use `{self.bot.prefix}hire` to hire them!",
          color = discord.Color.red()
          )
      else:
        last = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["clean"]
        td = timedelta(seconds=43200-currenttime+last)
        hour = td.seconds // 3600
        min = (td.seconds % 3600) // 60
        sec = td.seconds % 60
        clean = f"{hour} hours {min} minutes {sec} seconds"
        embed = discord.Embed(
          title =  bot_name,
          description = f"{cross} You cannot clean your shop too often! Try again in `{clean}`",
          color = discord.Color.red()
          )
    else:
      embed = discord.Embed(
       title =  bot_name,
       description = f"{cross} You do not own a dessert shop. Do `{self.bot.prefix}build` to build one!",
       color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)
  
  @commands.command()
  async def praise(self, ctx, user : discord.Member = None):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      if user is not None:
        cooldowns = self.bot.db["economy"]["users"][str(ctx.author.id)]["rep_cooldowns"]
        rep = self.bot.db["economy"]["users"][str(ctx.author.id)]["rep"]
        randrep = round(random.uniform(0.01, 0.08), 2)
        
        if ctx.author.id != user.id and not user.bot and str(user.id) in self.bot.db["economy"]["users"]:
          if str(user.id) in cooldowns and int(time.time()) - cooldowns[str(user.id)] < 86400:
            title, message, color = user, f"{cross} Looks like you have already praised this person in the past 24 hours... Try again later!", red
          else:
            await self.bot.user_stats(ctx, "praise")
            title, message, color = ctx.author, f"You praised **{user}** for their amazing dessert! \nTheir reputation increased by **{randrep} {erep}**!", green
            self.bot.db["economy"]["users"][str(user.id)]["rep"] += randrep
            self.bot.db["economy"]["users"][str(ctx.author.id)]["rep_cooldowns"][str(user.id)] = int(time.time())
        elif user.bot:
          title, message, color = "You can't praise bots ._.", f"Try praising someone else!", red
        elif str(user.id) not in self.bot.db["economy"]["users"]:
          title, message, color = "Shop not found!", f"{cross} That user doesn't seem to own a shop...", red
        else:
          title, message, color = "Self praise is a national disgrace!", f"Try praising someone else!", red   
      else:
        title, message, color = "Praise someone!", f"Praise someone and help them earn reputation stars! Use `{self.bot.prefix}praise <user>` to praise them!", green
      embed = discord.Embed(title = title, description = message, color = color)
    else:
      embed = discord.Embed(
       title =  bot_name,
       description = f"{cross} You do not own a dessert shop. Do `{self.bot.prefix}build` to build one!",
       color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)
  
  @praise.error
  async def praise_error(self, ctx, error):
    embed = discord.Embed(title = "Error", description = f"{cross} This user does not exist!", color = red)
    await ctx.reply(embed = embed, mention_author = False)
  @commands.command(aliases = ["d"])
  async def daily(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      last_daily = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["daily"]
      streak = self.bot.db["economy"]["users"][str(ctx.author.id)]["daily_streak"]
      curr_time = int(time.time())
      
  
      if curr_time - last_daily > 86400:
        xp = random.randint(1, 6)
        xp_msg, xp = await self.bot.check_xp(ctx, ctx.author.id, xp)
        income = await self.bot.get_income(ctx.author.id)
        emoji, streak_emoji, no_streak_emoji = "", "🟡", "⚫"
        if curr_time - last_daily > 86400 * 3:
          self.bot.db["economy"]["users"][str(ctx.author.id)]["daily_streak"] = 0
          streak = 0
        else:
          self.bot.db["economy"]["users"][str(ctx.author.id)]["daily_streak"] += 1
          streak + 1
  
        streak_bonus = int(income/100*streak * 3)
        daily_reward = income * 5
        self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["daily"] = curr_time
        self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] += daily_reward + streak_bonus
        
        for number in range(streak % 7):
          emoji += streak_emoji
        for number in range(7 - streak % 7):
          emoji += no_streak_emoji
        
        title, color = "Daily Reward", discord.Color.green()
        message = f"""**{tick} You have collected your daily reward of {daily_reward} {coin}**
  Streak Bonus: **{streak_bonus} {coin}**
  XP earned: **{xp} xp** {xp_msg}
  **__Daily Streak Progress__**
  {emoji}
  
  Current daily streak: **{streak}**
  Get a 7 daily streak for a reward!
  """
      else:
        td = timedelta(seconds=86400-curr_time+last_daily)
        hour = td.seconds // 3600
        min = (td.seconds % 3600) // 60
        sec = td.seconds % 60
        daily_cooldown = f"{hour} hours {min} minutes {sec} seconds"
        title, message, color = bot_name, f"{cross} You cannot claim your daily reward so soon! Try again in `{daily_cooldown}`",discord.Color.red()
    else:
      title, message, color = bot_name, f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one!",discord.Color.red()
      
    embed = discord.Embed(
        title = title,
        description = message,
      color = color
    )
    await ctx.reply(embed = embed, mention_author = False)
  
  @commands.command()
  async def monthly(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      level = self.bot.db["economy"]["users"][str(ctx.author.id)]["levels"]["level"]
      if level >= 10:
        last_monthly = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["monthly"]
        curr_time = int(time.time())
        if curr_time - last_monthly > 2592000:
          xp = random.randint(4, 20)
          xp_msg, xp = await self.bot.check_xp(ctx, ctx.author.id, xp)
          for i in range(10):
            xp_msg, dummy = await self.bot.check_xp(ctx, ctx.author.id, 0)
          income = await self.bot.get_income(ctx.author.id)
          monthly_reward = income * 24
          self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["monthly"] = curr_time
          self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] += monthly_reward
          bal = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
          title, color = "Monthly Reward", discord.Color.green()
          message = f"""**{tick} You have collected your monthly reward of {monthly_reward} {coin}**
  Balance: **{bal} {coin}**
  XP earned: **{xp} xp** {xp_msg}
  """
        else:
          td = timedelta(seconds=2592000-curr_time+last_monthly)
          days = td.days
          hour = td.seconds // 3600
          min = (td.seconds % 3600) // 60
          sec = td.seconds % 60
          monthly_cooldown = f"{days} days {hour} hours {min} minutes {sec} seconds"
          title, message, color = bot_name, f"{cross} You cannot claim your monthly reward so soon! Try again in `{monthly_cooldown}`",discord.Color.red()
      else:
        title, message, color = "Monthly Reward", f"{cross} You must be level 10 or higher to claim your monthly reward!" ,red
    else:
      title, message, color = bot_name, f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one!",discord.Color.red()
      
    embed = discord.Embed(
        title = title,
        description = message,
      color = color
    )
    await ctx.reply(embed = embed, mention_author = False)
  
  
  @commands.command(aliases = ["rh", "rush"])
  async def rushhour(self, ctx, number : int = None):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      rh = self.bot.db["economy"]["users"][str(ctx.author.id)]["rush_hour"]
      if number is None:
        title, color = "Rush Hour Info", discord.Color.green()
        message = f"Rush hour **instantly** gives you 6 hours worth of income. To use a rush hour coupon, you can use `{self.bot.prefix}rh <number of coupons>` \nYou currently have **{rh} coupons**"
      else:
        if 0 < number <= rh:
          title, color = bot_name, discord.Color.green()
          message = f"{cross} You do not have that many rush hour coupons! You can get them by using commands like `{self.bot.prefix}work` and participating in giveaways in the official {bot_name} server! \n`{self.bot.prefix}rh` for more information"
        else: 
          title, color = bot_name, discord.Color.red()
          if rh < 1:
            message = f"{cross} You do not have any rush hour coupons! You can get them by using commands like `{self.bot.prefix}work` and participating in giveaways in the official {bot_name} server! \n`{self.bot.prefix}rh` for more information"
          elif number < 1:
            message = f"{cross} Invalid number! Please use `{self.bot.prefix}rh <number of coupons>`"
          elif number > rh:
            message = f"You do not have that many coupons! You only have **{rh} coupons**"
    else:
      title, message, color = bot_name, f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one!",discord.Color.red()
      
    embed = discord.Embed(
        title = title,
        description = message,
      color = color
    )
    await ctx.reply(embed = embed, mention_author = False)

  # Hire Command
  @commands.command(aliases = ["employ"])
  async def hire(self, ctx, id = None):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      valid = "waiter", "cashier", "cleaner", "chef", "head", "manager"
      hire = {} 
      balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
      # Waiter
      hire["waiter"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["waiter"]
      hire["waiter_cost"] = int(100 * 1.4 ** hire["waiter"])
      hire["waiter_income"] = 10
      # Cashier
      hire["cashier"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["cashier"]
      hire["cashier_cost"] = int(250 * 1.4 ** hire["cashier"])
      hire["cashier_income"] = 20
      # Cleaner
      hire["cleaner"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["cleaner"]
      hire["cleaner_cost"] = int(100 * 1.3 ** hire["cleaner"])
      hire["cleaner_income"] = 50
      # Chef
      hire["chef"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["chef"]
      hire["chef_cost"] = int(6000 * 1.2 ** hire["chef"])
      hire["chef_income"] = 75
      # Head Chef
      hire["head_chef"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["head_chef"]
      hire["head_chef_cost"] = int(25000 * 1.23 ** hire["head_chef"])
      hire["head_chef_income"] = 150
      # Manager
      hire["manager"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["manager"]
      hire["manager_cost"] = int(100000 * 1.25 ** hire["manager"])
      hire["manager_income"] = 250
  
      # Max Upgrades Values
      hire["waiter_max"] = 12
      hire["cashier_max"] = 8
      hire["chef_max"] = 20
      hire["cleaner_max"] = 16
      hire["head_chef_max"] = 12
      hire["manager_max"] = 6
  
      if id is None:
        for item in valid:
          if item == "head":
            item = "head_chef"
          if hire[item] >= hire[item + "_max"]:
            hire[item + "_cost"] = "**Upgrade Maxed!**"
            hire[item + "_income"] = 0
        embed = discord.Embed(
          title = "Employees 👨‍🍳",
          description = f"""
  **Waiter** `({hire["waiter"]}/{hire["waiter_max"]})`
  Cost: {hire["waiter_cost"]} {coin}
  Income: +{hire["waiter_income"]} {coin}
  ID: `waiter`
  
  **Cashier** `({hire["cashier"]}/{hire["cashier_max"]})`
  Cost: {hire["cashier_cost"]} {coin}
  Income: +{hire["cashier_income"]} {coin}
  ID: `cashier`
  
  **Cleaner** `({hire["cleaner"]}/{hire["cleaner_max"]})`
  Cost: {hire["cleaner_cost"]} {coin}
  Income: +{hire["cleaner_income"]} {coin}
  ID: `cleaner`
  
  **Chef** `({hire["chef"]}/{hire["chef_max"]})`
  Cost: {hire["chef_cost"]} {coin}
  Income: +{hire["chef_income"]} {coin}
  ID: `chef`
  
  **Head Chef** `({hire["head_chef"]}/{hire["head_chef_max"]})`
  Cost: {hire["head_chef_cost"]} {coin}
  Income: +{hire["head_chef_income"]} {coin}
  ID: `head`
  
  **Manager** `({hire["manager"]}/{hire["manager_max"]})`
  Cost: {hire["manager_cost"]} {coin}
  Income: +{hire["manager_income"]} {coin}
  ID: `manager`
  **_\_\__\__\__\__\__\__\__\__\__\_\__\__\__\__\__\_\_\_\_**
  Balance: **{balance:,} {coin}**
  Hire more staff using `{self.bot.prefix}hire <ID>`
  """,
        color = discord.Color.blurple()
        )
      elif id in valid:
        if id == "head":
          id = "head_chef"
        if balance >= hire[id+"_cost"] and hire[id] < hire[id+"_max"]:
          self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] -= hire[id+"_cost"]
          self.bot.db["economy"]["users"][str(ctx.author.id)]["income"] += hire[id+"_income"]
          self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"][id] += 1
          balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
          income = await self.bot.get_income(ctx.author.id)
          cost = hire[id+"_cost"]
          if id == "head_chef":
            id = "head chef"
          embed = discord.Embed(
            title = "Employees",
            description = f"{tick} You have employed a **{id}** for **{cost} {coin}**! \nBalance: **{balance:,} {coin}** \nIncome: **{income:,} {coin}**", 
            color = discord.Color.green()
          )
        elif hire[id] >= hire[id+"_max"]:
          if id == "head_chef":
            id = "head chef"
          embed = discord.Embed(
            title = "Employees",
            description = f"{cross} You cannot employ so many {id}s!",
            color = discord.Color.red()
          )
        elif balance < hire[id+"_cost"]:
          if id == "head_chef":
            id = "head chef"
          embed = discord.Embed(
            title = "Employees",
            description = f"{cross} You do not have enough money to hire a {id}",
            color = discord.Color.red()
          )
        
      else:
        embed = discord.Embed(title = "Employees", description = f"{cross} Invalid ID! Please use `{self.bot.prefix}hire <ID>`", color = discord.Color.red())
    else:
      embed = discord.Embed(
        title = bot_name,
        description = f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one!",
      color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)
  
  # Upgrades Command
  @commands.command(aliases = ["up", "upgrades"])
  async def upgrade(self, ctx, id = None):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      valid = ["tipjar", "sign", "paint", "fan", "aircon", "light"]
      upgrades = {} 
      balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
      # "upgrade" : {"tipjar" : 0, "sign" : 0, "paint" : 0, "fan" : 1, "aircon" : 0, "light" : 0}
      # Tip Jar
      upgrades["tipjar"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["upgrade"]["tipjar"]
      upgrades["tipjar_cost"] = int(100 * 1.75 ** upgrades["tipjar"])
      upgrades["tipjar_income"] = 10
      # Sign
      upgrades["sign"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["upgrade"]["sign"]
      upgrades["sign_cost"] = int(250 * 1.5 ** upgrades["sign"])
      upgrades["sign_income"] = 50
      # Paint
      upgrades["paint"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["upgrade"]["paint"]
      upgrades["paint_cost"] = int(200 * 1.3 ** upgrades["paint"])
      upgrades["paint_income"] = 25
      # Fan
      upgrades["fan"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["upgrade"]["fan"]
      upgrades["fan_cost"] = int(450 * 1.2 ** upgrades["fan"])
      upgrades["fan_income"] = 150
      # Aircon
      upgrades["aircon"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["upgrade"]["aircon"]
      upgrades["aircon_cost"] = int(8000 * 1.2 ** upgrades["aircon"])
      upgrades["aircon_income"] = 600
      # Lights
      upgrades["light"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["upgrade"]["light"]
      upgrades["light_cost"] = int(10000 * 1.2 ** upgrades["light"])
      upgrades["light_income"] = 1250
  
      # Max Upgrades Values
      upgrades["tipjar_max"] = 5
      upgrades["sign_max"] = 2
      upgrades["paint_max"] = 6
      upgrades["fan_max"] = 8
      upgrades["aircon_max"] = 8
      upgrades["light_max"] = 8
  
      if id is None:
        for item in valid:
          if upgrades[item] >= upgrades[item + "_max"]:
            upgrades[item + "_cost"] = "**Upgrade Maxed!**"
            upgrades[item + "_income"] = 0
        embed = discord.Embed(
          title = "Upgrades",
          description = f"""
  **Cooler Tip Jar** `({upgrades["tipjar"]}/{upgrades["tipjar_max"]})`
  Cost: {upgrades["tipjar_cost"]} {coin}
  Income: +{upgrades["tipjar_income"]} {coin}
  ID: `tipjar`
  
  **Open/Close Sign** `({upgrades["sign"]}/{upgrades["sign_max"]})`
  Cost: {upgrades["sign_cost"]} {coin}
  Income: +{upgrades["sign_income"]} {coin}
  ID: `sign`
  
  **Better Paint** `({upgrades["paint"]}/{upgrades["paint_max"]})`
  Cost: {upgrades["paint_cost"]} {coin}
  Income: +{upgrades["paint_income"]} {coin}
  ID: `paint`
  
  **More Fans** `({upgrades["fan"]}/{upgrades["fan_max"]})`
  Cost: {upgrades["fan_cost"]} {coin}
  Income: +{upgrades["fan_income"]} {coin}
  ID: `fan`
  
  **Stronger Air Cons** `({upgrades["aircon"]}/{upgrades["aircon_max"]})`
  Cost: {upgrades["aircon_cost"]} {coin}
  Income: +{upgrades["aircon_income"]} {coin}
  ID: `aircon`
  
  **Better Lights** `({upgrades["light"]}/{upgrades["light_max"]})`
  Cost: {upgrades["light_cost"]} {coin}
  Income: +{upgrades["light_income"]} {coin}
  ID: `light`
  **\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**
  Balance: **{balance} {coin}**
  Upgrading items will increase your tips!
  Use `{self.bot.prefix}upgrade <ID>` to upgrade an item!
  """,
          color = discord.Color.blurple()
        )
      elif id in valid:
        if balance >= upgrades[id+"_cost"] and upgrades[id] < upgrades[id+"_max"]:
          self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] -= upgrades[id+"_cost"]
          self.bot.db["economy"]["users"][str(ctx.author.id)]["income"] += upgrades[id+"_income"]
          self.bot.db["economy"]["users"][str(ctx.author.id)]["upgrade"][id] += 1
          balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
          income = await self.bot.get_income(ctx.author.id)
          self.bot.db["economy"]["users"][str(ctx.author.id)]["tips"] += 50 * upgrades[id]
            
          cost = upgrades[id+"_cost"]
          if id == "paint":
            msg = f"You have applied a new coat of {id}"
          if id == "tipjar":
            msg = f"You have purchased a cooler tip jar"
          else:
            if id == "light":
              id = "lights"
            if id == "fan":
              id = "fans"
            if id == "sign":
              id = "open/close sign"
            msg = f"You have upgraded your **{id}**"
          embed = discord.Embed(
            title = "Shop Upgrades",
            description = f"{tick} {msg} for **{cost} {coin}**! \nBalance: **{balance:,} {coin}** \nIncome: **{income:,} {coin}** \nYour tips have increased!", 
            color = discord.Color.green()
          )
        elif balance < upgrades[id+"_cost"]:
          if id == "light":
              id = "lights"
          if id == "fan":
            id = "fans"
          if id == "sign":
            id = "open/close sign"
          embed = discord.Embed(
            title = "Shop Upgrades",
            description = f"{cross} You do not have enough money to upgrade your {id}",
            color = discord.Color.red()
          )
        elif upgrades[id] >= upgrades[id+"_max"]:
          if id == "light":
              id = "lights"
          if id == "fan":
            id = "fans"
          if id == "sign":
            id = "open/close sign"
          grammer = "are" if id[-1] == "s" else "is"
          embed = discord.Embed(
            title = "Shop Upgrades",
            description = f"{cross} Your **{id}** {grammer} already fully upgraded!",
            color = discord.Color.red()
          )
      else:
        embed = discord.Embed(
          title = bot_name,
          description = f"{cross} Invalid ID!",
          color = discord.Color.red()
        )
  
    else:
      embed = discord.Embed(
        title = bot_name,
        description = f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one!",
      color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)
  
  @commands.command(aliases = ["boosts"])
  async def boost(self, ctx, id = None, bulk = None):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      user = str(ctx.author.id)
      balance = self.bot.db["economy"]["users"][user]["balance"]
      boost = {}
      #"boost" : {"band" : 0, "piano" : 0, "guitarist" : 0, "singer" : 0, "magician" : 0}
      # Singer
      boost["singer"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"]["singer"]
      boost["singer_cost"] = 500
      boost["singer_income"] = 1000
      boost["singer_duration"] = 2
  
      # Guitarist
      boost["guitarist"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"]["guitarist"]
      boost["guitarist_cost"] = 8000
      boost["guitarist_income"] = 10000
      boost["guitarist_duration"] = 3
  
      # Pianist
      boost["pianist"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"]["pianist"]
      boost["pianist_cost"] = 2500
      boost["pianist_income"] = 4000
      boost["pianist_duration"] = 4
  
      # Band
      boost["band"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"]["band"]
      boost["band_cost"] = 10000
      boost["band_income"] = 4000
      boost["band_duration"] = 6
  
      # Magician
      boost["magician"] = self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"]["magician"]
      boost["magician_cost"] = 10000
      boost["magician_income"] = 8000
      boost["magician_duration"] = 2
      if id is None:
        embed = discord.Embed(
          title = "Shop Boosts",
          description = f"""
  **__Singer__** `[2h]`
  Boost: **+ 1000 {coin} / hour**
  Cost: **500 {coin}**
  ID: `singer`
  
  **__Guitarist__** `[3h]`
  Boost: **+ 5000 {coin} / hour**
  Cost: **8000 {coin} / hour**
  ID: `guitarist`
          
  **__Pianist__** `[4h]`
  Boost: **+ 2500 {coin} / hour**
  Cost: **4000 {coin}**
  ID: `pianist`
    
  **__Band__** `[6h]`
  Boost: **+ 10,000 {coin} / hour**
  Cost: **40,000 {coin}**
  ID: `band`
  
  **__Magician__** `[2h]`
  Boost: **+ 8000 {coin} / hour**
  Cost: **10,000 {coin}**
  ID: `magician`
  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
  Balance: **{balance} {coin}**
  Use `{self.bot.prefix}boost <ID>` to purchase a boost.
  Use `{self.bot.prefix}boost view` to view your current boosts.
  """,
          color = discord.Color.purple()
        )
      elif id == "view":
        boosts = {}
        for boost in self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"]:
          boosts[boost] = self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"][boost]
        embed = discord.Embed(
          title = ":hourglass: | Active Boosters",
          color = discord.Color.teal()
        )
        for boost in self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"]:
          embed.add_field(name = f"**{boost.title()}:** ", value = f"Time Left: **{boosts[boost]} hour(s)**", inline = False)
      elif id in ("band", "pianist", "guitarist", "singer", "magician"):
        if bulk is None:
          bulk = 1
        try:
          bulk = int(bulk)
          if bulk < 1:
            a
        except:
          embed = discord.Embed(
            title = "🚀 | Boosts",
            description = f"{cross} Invalid amount! Please use `{self.bot.prefix}boosts <ID> <amount>`!",
            color = discord.Color.red()
          )
          await ctx.reply(embed = embed, mention_author = False)
          return
        if self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"][id] > 48 or bulk > 5:
          if self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"][id] > 48:
            message = f"{cross} You cannot buy more boosts when you have more than 48 hours of boosts remaining!"
          else:
            message = "You cannot by more than 5 boosts at one time!"
          embed = discord.Embed(
            title = "🚀 | Boosts",
            description = message,
            color = discord.Color.red()
          )
          await ctx.reply(embed = embed, mention_author = False)
          return
        if balance >= boost[id+"_cost"] * bulk:
          self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] -= boost[id+"_cost"] * bulk
          self.bot.db["economy"]["users"][str(ctx.author.id)]["boost"][id] += boost[id+"_duration"] * bulk
          balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
          duration = boost[id+"_duration"] * bulk
          embed = discord.Embed(
          title = "🚀 | Boosts",
          description = f"{tick} You have hired a **{id}** for **{duration} hours** \nBalance: **{balance} {coin}** \nIncome: **{await self.bot.get_income(ctx.author.id):,} {coin}/ hour**",
          color = discord.Color.green()
        )
        else:
          embed = discord.Embed(
          title = "🚀 | Boosts",
          description = f"{cross} You do not have enough money to hire **{bulk} {id}**  \nBalance: **{balance} {coin}** ",
          color = discord.Color.red()
        )
      else:
        embed = discord.Embed(
          title = "Shop Boosts",
          description = f"{cross} Invalid ID! Please use `{self.bot.prefix}boost <id>`",
          color = discord.Color.red()
        )
    else:
      embed = discord.Embed(
        title = bot_name,
        description = f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one!",
      color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)

async def setup(bot):
  await bot.add_cog(Economy(bot))