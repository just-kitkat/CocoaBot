import discord, time, psutil
from vars import *
from datetime import timedelta, date, datetime
from discord.ext import commands

class Info(commands.Cog, name = "Statistics Commands"):

  def __init__(self, bot):
    self.bot = bot

  

  @commands.command()
  async def ping(self, ctx):
    "Gets the bot's latency"
    ping = round(self.bot.latency * 1000)
    embed = discord.Embed(title = bot_name, 
                         description = f"Ping: **{ping}ms** \nResponse time: **Calculating...**",
                         color = red)
    start = time.time()
    msg = await ctx.reply(embed = embed, mention_author = False)
    end = time.time()
    response_time = round((end - start) * 1000)
    updated_embed = discord.Embed(title = bot_name,
                                 description = f"Ping: **{ping}ms** \nResponse time: **{response_time}ms**",
                                 color = green)
    await msg.edit(embed = updated_embed)

  # Info Command
  @commands.command(aliases = ["about"])
  async def info(self, ctx):
    "Get bot's statistics"
    users = len(self.bot.db["economy"]["users"])
    guilds = len(list(self.bot.guilds))
    ram = psutil.virtual_memory()[2]
    cpu = psutil.cpu_percent()
    embed = discord.Embed(
      title = f"{bot_name} Information",
      color = discord.Color.green()
    )
    embed.add_field(name = "**👥 Users**", value = "∟ " + f"{users:,}", inline = True)
    embed.add_field(name = "**💳 Guilds**", value = "∟ " + f"{guilds:,}", inline = True)
    embed.add_field(name = "**👑 Creator**", value = "∟ kitkat3141#0422" , inline = True)
    embed.add_field(name = "**💻 Memory used**", value = "∟ " + str(ram) + "MB", inline = True)
    embed.add_field(name = "**📇 Cpu**", value = "∟ " + str(cpu) + "%", inline = True)
    await ctx.reply(embed = embed, mention_author = False)

  # Balance Command
  @commands.command(aliases = ["bal"])
  async def balance(self, ctx, member : discord.Member = None):
    """Get a user's balance"""
    if member is None: 
      user = ctx.author.id
    else:
      user = member.id
    if str(user) in self.bot.db["economy"]["users"]:
      balance = self.bot.db["economy"]["users"][str(user)]["balance"]
      #income = self.bot.db["economy"]["users"][str(user)]["income"]
      income = await self.bot.get_income(user, True)  
      happiness = self.bot.db["economy"]["users"][str(user)]["happiness"]
      rep = self.bot.db["economy"]["users"][str(user)]["rep"]
      embed = discord.Embed(
        title = f"Balance",
        description = f"Balance: **{balance:,} {coin}** \nIncome: **{income} {coin} / hour** \nReputation: **{rep} {erep}** \nHappiness: **{happiness}%**",
        color = discord.Color.green()
      )
    else:
      if member is None:
        name = "You"
      else:
        name = member.name
      embed = discord.Embed(
        title = bot_name,
        description = f"{cross} {name} do not own a dessert shop. Use `{self.bot.prefix}build` to build one",
        color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)

  @balance.error
  async def bal_error(self, ctx, error):
    embed = discord.Embed(
      title = bot_name,
      description = f"{cross} User not found! ",
      color = discord.Color.red()
    )
    await ctx.reply(embed = embed, mention_author = False)


  # Stats Command
  @commands.command(aliases = ["stat", "statistic", "statistics", "profile"])
  async def stats(self, ctx, member : discord.Member = None):
    if member is None:
      member = ctx.author
    if str(member.id) in self.bot.db["economy"]["users"]:
      balance = self.bot.db["economy"]["users"][str(member.id)]["balance"]
      xp_mult = self.bot.db["economy"]["users"][str(member.id)]["levels"]["xp_mult"]
      income = self.bot.db["economy"]["users"][str(member.id)]["income"]
      happiness = self.bot.db["economy"]["users"][str(member.id)]["happiness"]
      rep = self.bot.db["economy"]["users"][str(member.id)]["rep"]
      cmd_count = self.bot.db["economy"]["users"][str(member.id)]["stats"]
      work, tip, clean, praise, overtime = cmd_count["work"], cmd_count["tip"], cmd_count["clean"], cmd_count["praise"], cmd_count["overtime"]
      
      
      account_age = self.bot.db["economy"]["users"][str(member.id)]["account_created"]
      td = (int(time.time()) - account_age) // 86400
  
      xp_emoji = "🟩"
      no_xp_emoji = "⬛"
      xp = self.bot.db["economy"]["users"][str(member.id)]["levels"]["xp"]
      level = self.bot.db["economy"]["users"][str(member.id)]["levels"]["level"]
      xp_needed = self.bot.db["economy"]["users"][str(member.id)]["levels"]["xp_needed"]
      emoji = ""
      levels = int(xp/xp_needed * 10)
      for i in range(0, levels):
        emoji += xp_emoji
      for i in range(0, 10 - levels):
        emoji += no_xp_emoji
      warning = ""
      if happiness < 50:
        warning = f"\n`Your customer happiness is very low and it will affect your hourly income! Use {self.bot.prefix}clean to clean your shop!`"
        happiness_emoji = " :pensive:"
      elif happiness > 80:
        happiness_emoji = " :grin:"
      else:
        happiness_emoji = " :smile:"
      
      embed = discord.Embed(
        title = f"{member}'s Statistics",
        description = f"""
  Balance: **{balance:,}**
  Income: **{income:,}/hr**
  Reputation: **{rep} {erep}**
  Level: **{level}** ({xp_mult}x)
  {emoji} `({xp} / {xp_needed})`
  
  __Happiness:__  
  **{happiness}% {happiness_emoji}**
  
  __Command Stats:__
  Work: **{work}**
  Tip: **{tip}**
  Clean: **{clean}**
  Praise: **{praise}**
  Overtime: **{overtime}** (Coming Soon!)
        
  __Shop Age:__
  **{td} days** {warning}
  """,
        color = discord.Color.green(),
        timestamp = datetime.utcnow()
      )
    else:
      if member == ctx.author.id:
        msg = "You do not"
      else:
        msg = "That user does not"
      embed = discord.Embed(
        title = bot_name,
        description = f"{cross} {msg} own a dessert shop. Use `{self.bot.prefix}build` to build one!",
      color = discord.Color.red()
      )
    await ctx.reply(embed = embed, mention_author = False)
  
  @stats.error
  async def stats_error(self, ctx, error):
    embed = discord.Embed(
      title = bot_name,
      description = f"{cross} User not found! ",
      color = discord.Color.red()
    )
    await ctx.reply(embed = embed, mention_author = False)

async def setup(bot):
  await bot.add_cog(Info(bot))