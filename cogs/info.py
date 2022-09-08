import discord, time, math
from datetime import timedelta
from vars import *
from errors import *
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog, name = "Information Commands"):

  def __init__(self, bot):
    self.bot = bot


  @commands.hybrid_command()
  async def ping(self, ctx):
    """Gets the bot's latency"""
    ping = round(self.bot.latency * 1000)
    embed = discord.Embed(title = bot_name, 
                         description = f"Ping: **{ping}ms** \nResponse time: **Calculating...**",
                         color = red)
    start = time.time()
    msg = await ctx.reply(embed = embed, mention_author = False)
    end = time.time()
    responsetime = round((end - start) * 1000)
    updated_embed = discord.Embed(title = bot_name,
                                 description = f"Ping: **{ping}ms** \nResponse time: **{responsetime}ms**",
                                 color = green)
    await msg.edit(embed = updated_embed)


    
async def setup(bot):
  await bot.add_cog(Info(bot))