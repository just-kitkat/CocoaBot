import discord, time, random, math
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
"balance" : 1000, "income" : 500, "tips" : 200, "account_created" : int(_time.time()), "happiness" : 100, "daily_streak" : 0, "rush_hour" : 0, "guild" : "", "rep" : 0.00, "rep_cooldowns" : {}, #{user_id : time}
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
      user = bot.get_user(ctx.author.id)
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


async def setup(bot):
  await bot.add_cog(Economy(bot))