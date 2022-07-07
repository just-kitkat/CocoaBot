import discord
from vars import *
from discord.ext import commands

class Misc(commands.Cog, name = "Miscellaneous Commands"):

  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases = ["lb", "leaderboards"])
  @commands.cooldown(4, 60, commands.BucketType.user)
  async def leaderboard(self, ctx, arg = ""):
    lb_dump = {}
    try:
      arg = arg.lower()
    except:
      pass
    for user in self.bot.db["economy"]["users"]:
      if arg in ("rep", "reputation"):
        lb_dump[user] = self.bot.db["economy"]["users"][user]["rep"]
        emoji = erep
      elif arg in ("level", "levels"):
        lb_dump[user] = self.bot.db["economy"]["users"][user]["levels"]["level"]
        emoji = "⚡"
      elif arg in ("income", "incomes"):
        lb_dump[user] = self.bot.db["economy"]["users"][user]["income"]
        emoji = f"{coin} / hr"
      else:
        lb_dump[user] = self.bot.db["economy"]["users"][user]["balance"]
        emoji = coin
    lb = {users: balance for users, balance in reversed(sorted(lb_dump.items(), key=lambda item: item[1]))}
    
    count = 1
    msg = ""
    for user in lb:
      guild = self.bot.db["economy"]["users"][user]["guild"]
      tag = f"**[" + self.bot.db["economy"]["guild"][guild]["tag"] + "]**" if guild != "" and self.bot.db["economy"]["guild"][guild]["tag"] != "" else ""
        
      bal = lb[user]
      user = self.bot.get_user(int(user))
      msg += f"**{count}.** {tag} {user}: **{bal:,} {emoji}** \n"
      if count == 1 and user == ctx.author: await self.bot.check_achievements(ctx, True)
      count += 1
      if count > 10: break
        
    embed = discord.Embed(title = "Leaderboards", description = msg, color = green)
    await ctx.send(embed = embed)

  @commands.command()
  async def tutorial(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      embed = discord.Embed(
        title = f"{bot_name} Tutorial",
        description = f"""
Welcome to your very own dessert shop! You will get an hourly income to help manage your shop!

Bot prefix: `{self.bot.prefix}`
Shop Commands:
➼ build - Build a shop
➼ work - Make some desserts and earn cash
➼ tips - Let's you collect tips every 5 minutes
➼ clean - Clean up your shop to keep your customers happy
➼ location - View your shop location
➼ cooldowns - View your command cooldowns
➼ upgrades - View all available upgrades
➼ ads - View all available advertisements
➼ hire - View all available staff to hire
➼ stats - View your current statistics

**Tips and Tricks:**
➼ Clean your shop every 6 hours to maximise hourly income!
➼ Use `{self.bot.prefix}cooldowns` to view all your current cooldowns

Join the official **{bot_name}** server here: https://discord.gg/5aNRWDj97u
""",
        color = discord.Color.green()
      )
    else:
      embed = discord.Embed(
        title = bot_name,
        description = f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one",
        color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)

  @commands.command()
  async def level(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      level = self.bot.db["economy"]["users"][str(ctx.author.id)]["levels"]["level"]
      xp = self.bot.db["economy"]["users"][str(ctx.author.id)]["levels"]["xp"]
      xp_needed = self.bot.db["economy"]["users"][str(ctx.author.id)]["levels"]["xp_needed"]
      
      title, color = "Leveling Rewards", green
      msg = f"""
Level 2: **1000 {coin} Reward**
Level 5: **10,000 {coin} Reward**
Level 10: **Access to monthly Rewards**
Level 20: **Access to Expeditions** (Coming soon!)
Level 30: **1,000,000 {coin} Reward**
"""
    else:
      title,msg,color = bot_name, f"{cross} You do not own a dessert shop. Do `{self.bot.prefix}build` to build one!", discord.Color.red()
    embed = discord.Embed(
      title = title,
      description = msg,
      color = color
    )
    await ctx.reply(embed = embed, mention_author = False)

  @commands.command(aliases = ["c", "cooldown"])
  async def cooldowns(self, ctx):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      balance = self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"]
      balance_f = await get_data("balance", ctx.author.id)
      daily = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["daily"]
      work = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["work"]
      tip = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["tip"]
      clean = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["clean"]
      monthly = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["monthly"]
      current_time = int(_time.time())
      if int(_time.time()) - work > 600:
        work = tick + " **READY**"
      else:
        last = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["work"]
        min = str(math.floor((10 - ((current_time - last) % 3600) / 60)))
        sec = str(math.floor((60 - ((current_time - last) % 3600) % 60)))
        work = cross + f" {min} minutes {sec} seconds"
      if int(_time.time()) - tip > 300:
        tip = tick + " **READY**"
      else:
        last = self.bot.db["economy"]["users"][str(ctx.author.id)]["cooldowns"]["tip"]
        min = str(math.floor((5 - ((current_time - last) % 3600) / 60)))
        sec = str(math.floor((60 - ((current_time - last) % 3600) % 60)))
        tip = cross + f" {min} minutes {sec} seconds"
      if int(_time.time()) - clean > 21600:
        clean = tick + " **READY**"
      else:
        td = timedelta(seconds=43200-current_time+clean)
        hour = td.seconds // 3600
        min = (td.seconds % 3600) // 60
        sec = td.seconds % 60
        clean = cross + f" {hour} hours {min} minutes {sec} seconds"
      if int(_time.time()) - daily > 86400:
        daily = tick + " **READY**"
      else:
        td = timedelta(seconds=86400-current_time+daily)
        hour = td.seconds // 3600
        min = (td.seconds % 3600) // 60
        sec = td.seconds % 60
        daily = cross + f" {hour} hours {min} minutes {sec} seconds"
      if int(_time.time()) - monthly > 86400*30:
        monthly = tick + " **READY**"
      else:
        td = timedelta(seconds=86400*30-current_time+monthly)
        days = td.days
        hour = td.seconds // 3600
        min = (td.seconds % 3600) // 60
        sec = td.seconds % 60
        monthly = cross + f" {days} days {hour} hours {min} minutes {sec} seconds"
        
      embed = discord.Embed(
       title = f"⏱️ Cooldowns | {bot_name}",
       description = f"""
  **Tip:** 
  {tip} 
  
  **Work:** 
  {work} 
  
  **Clean:** 
  {clean}
  
  **Daily:** 
  {daily}
  
  **Monthly:** 
  {monthly}
  
  **Vote:**
  ⛔︎ **DISABLED**
  **\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**
  Balance: **{balance_f} {coin}**
  """,
       color = discord.Color.gold()
      )
    else:
      embed = discord.Embed(
       title =  bot_name,
       description = f"{cross} You do not own a dessert shop. Do `{self.bot.prefix}build` to build one!",
       color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)

  @commands.command(aliases = ["achievement", "achieve"])
  async def achievements(self, ctx, user = None):
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      user_stats = self.bot.db["economy"]["users"][str(ctx.author.id)]["stats"]
      achievements = self.bot.db["economy"]["users"][str(ctx.author.id)]["achievements"]
      millionaire = tick if self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] >= 1000000 else cross
      work = tick if user_stats["work"] >= 100 else cross
      tip = tick if user_stats["tip"] >= 100 else cross
      clean = tick if user_stats["praise"] >= 25 else cross
      praise = tick if user_stats["praise"] >= 100 else cross
      manager = tick if self.bot.db["economy"]["users"][str(ctx.author.id)]["hire"]["manager"] >= 1 else cross
      leaderboard = tick if self.bot.db["economy"]["users"][str(ctx.author.id)]["achievements"]["leaderboard"] else cross
      million = tick if self.bot.db["economy"]["users"][str(ctx.author.id)]["achievements"]["million"] else cross
      guild = tick if achievements["guild"] else cross
      
      title, color = "Achivements", discord.Color.teal()
      message = f"""
  Millionaire: **Reach 1,000,000 {coin}** 
  Reward: **Massive sums of XP** | Status: {million}
      
  Workaholic: **Work 100 Times**
  Reward: **1,000,000 {coin}** | Status: {work}
      
  How Wonderfully Delicious: **Collect Tips 100 Times** 
  Reward: **5 {erep}** | Status: {tip}
      
  Encourager: **Praise Others a Total of 100 Times** 
  Reward: **100,000 {coin}** | Status: {praise}
      
  What a clean place: **Clean Your Shop 25 Times**
  Reward: **2,000 {coin}** | Status: {clean}
      
  I'm not the manager?: **Hire a Manager** 
  Reward: **10,000 {coin}** | Status: {manager}
      
  Top of the world: **Get First Place on the Leaderboard** 
  Reward: **10 {erep}** | Status: {leaderboard}
      
  A Place To Call Home: **Join a Guild** 
  Reward: **0.25x XP Multiplier** | Status: {guild}
  """
    else:
      title, message, color = bot_name, f"{cross} You do not own a dessert shop. Use `{prefix}build` to build one!",discord.Color.red()
    embed = discord.Embed(title = title, description = message, color = color)
    embed.set_footer(text = "This command is still in beta and might not fully work yet!")
    await ctx.reply(embed = embed, mention_author = False)


async def setup(bot):
  await bot.add_cog(Misc(bot))