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


def setup(bot):
  bot.add_cog(Misc(bot))