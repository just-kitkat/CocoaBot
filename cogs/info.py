import discord, time, math
from datetime import timedelta
from vars import *
from errors import *
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog, name = "Information Commands"):

  def __init__(self, bot):
    self.bot = bot


  @app_commands.command()
  async def ping(self, itx: discord.Interaction):
    """Gets the bot's latency"""
    ping = round(self.bot.latency * 1000)
    embed = discord.Embed(title = bot_name, 
                         description = f"Ping: **{ping}ms** \nResponse time: **Calculating...**",
                         color = red)
    start = time.time()
    msg = await itx.response.send_message(embed = embed)
    end = time.time()
    responsetime = round((end - start) * 1000)
    updated_embed = discord.Embed(title = bot_name,
                                 description = f"Ping: **{ping}ms** \nResponse time: **{responsetime}ms**",
                                 color = green)
    await itx.edit_original_response(embed = updated_embed)


    
async def setup(bot):
  await bot.add_cog(Info(bot))