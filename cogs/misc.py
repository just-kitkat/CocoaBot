import discord
from vars import *
from discord.ext import commands

class Misc(commands.Cog, name = "Miscellaneous Commands"):

  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases = ["lb", "leaderboards"])
  @commands.cooldown(4, 60, commands.BucketType.user)
  async def leaderboard(self, ctx, arg = None):
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

async def setup(bot):
  await bot.add_cog(Misc(bot))