import discord, time, random, math
from vars import *
from datetime import timedelta, date, datetime
from discord.ext import commands

class Economy(commands.Cog, name = "General Commands"):

  def __init__(self, bot):
    self.bot = bot

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
          notify = f"\nYour customers' happiness is at **{happiness}%**. This will affect your income significantly! Please clean your shop using `{prefix}clean`"
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
       description = f"{cross} You do not own a dessert shop. Do `{prefix}build` to build one!",
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
       description = f"{cross} You do not own a dessert shop. Do `{prefix}build` to build one!",
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
          description = f"{cross} You did not employ any cleaners! Use `{prefix}hire` to hire them!",
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
       description = f"{cross} You do not own a dessert shop. Do `{prefix}build` to build one!",
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
        title, message, color = "Praise someone!", f"Praise someone and help them earn reputation stars! Use `{prefix}praise <user>` to praise them!", green
      embed = discord.Embed(title = title, description = message, color = color)
    else:
      embed = discord.Embed(
       title =  bot_name,
       description = f"{cross} You do not own a dessert shop. Do `{prefix}build` to build one!",
       color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)
  
  @praise.error
  async def praise_error(self, ctx, error):
    embed = discord.Embed(title = "Error", description = f"{cross} This user does not exist!", color = red)
    await ctx.reply(embed = embed, mention_author = False)


def setup(bot):
  bot.add_cog(Economy(bot))