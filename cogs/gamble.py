import discord, time, random, math

from vars import *
from errors import *
from typing import Literal
from discord import app_commands
from discord.ext import commands

class Gamble(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    
  @factory_check()
  @app_commands.command(name = "coinflip")
  async def coinflip(self, itx: discord.Interaction, bet: Literal["heads", "tails"], amt:int):
    """Flip a coin and earn rewards! Good luck!!"""
    max_bet = math.floor(self.bot.db["economy"][str(itx.user.id)]["balance"] / 2)
    color = red
    if amt > max_bet:
      msg = f"You cannot bet that much! You can only bet half your current balance!"
    elif amt > 200000:
      msg = f"You can only bet a maximum of **200,000{coin}!**"
    elif amt < 0:
      msg = f"Why are you betting a negative value? Please bet a positive value! `{self.bot.prefix}coinflip <heads/tails> <amount>.`"
    elif amt == 0:
      msg = f"Nice try but CocoaBot cannot be fooled! Please make sure your bet is more than 0{coin}! `{self.bot.prefix}coinflip <heads/tails> <amount>.`"
    else:
      last_cf = self.bot.db["economy"][str(itx.user.id)]["last_cf"]
      currenttime = int(time.time())
      mins_left = str(math.floor((10 - ((currenttime - last_cf) % 3600) / 60)))
      secs_left = str(math.floor((60 - ((currenttime - last_cf) % 3600) % 60)))
      if int(time.time()) >= last_cf + 600:
        if bet in ("h", "head", "heads", "t", "tail", "tails"):
          if bet in ("h", "head", "heads"):
            cf_bet = "heads"
          elif bet in ("t", "tail", "tails"):
            cf_bet = "tails"
          result = random.choice(["heads", "tails"])
          if result == cf_bet:
            self.bot.db["economy"][str(itx.user.id)]["balance"] += amt
            msg, color = f"The coin landed on **{cf_bet}**! You have earned **{amt}{coin}**", green
          else:
            self.bot.db["economy"][str(itx.user.id)]["balance"] -= amt
            msg = f"The coin landed on **{result}**. You have lost **{amt}{coin}**"
          self.bot.db["economy"][str(itx.user.id)]["last_cf"] = int(time.time())
        else:
          msg = f"Please choose either heads or tails! `{self.bot.prefix}coinflip <heads/tails> <amount>`."
      else: 
        msg = f"Doing too many coinflips will make your fingers tired! Try again in `{mins_left}m {secs_left}s`"
    embed = discord.Embed(title = "Coinflip", description = msg, color = color)
    await itx.response.send_message(embed = embed)


async def setup(bot):
  await bot.add_cog(Gamble(bot))