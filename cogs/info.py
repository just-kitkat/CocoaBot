import discord
import time
import math
import psutil
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

  @commands.hybrid_command(aliases = ["about"])
  async def info(self, ctx):
    "Get bot's statistics"
    users = len(self.bot.db["economy"])
    guilds = len(list(self.bot.guilds))
    uptime = (int(time.time()) - self.bot.cache["uptime"])
    td = timedelta(seconds=uptime)
    hour = td.seconds // 3600
    min = (td.seconds % 3600) // 60
    sec = td.seconds % 60
    uptime = f"{hour}h {min}m {sec}s"
    ram = psutil.virtual_memory()[2]
    cpu = psutil.cpu_percent()
    cmds_ran = self.bot.dbo["others"]["total_commands_ran"]
    embed = discord.Embed(
      title = f"{bot_name} Information",
      description = adv_msg,
      color = discord.Color.green()
    )
    embed.add_field(name = "**👥 Users**", value = "∟ " + f"{users:,}", inline = True)
    embed.add_field(name = "**💳 Guilds**", value = "∟ " + f"{guilds:,}", inline = True)
    embed.add_field(name = "**👑 Creator**", value = "∟ kitkat3141#0422" , inline = True)
    embed.add_field(name = "**💻 Memory used**", value = f"∟ {ram}MB", inline = True)
    embed.add_field(name = "**📇 Cpu**", value = f"∟ {cpu}%", inline = True)
    
    embed.add_field(name = "**🤖 Commands ran**", value = f"∟ {cmds_ran:,}", inline = True)
    embed.add_field(name = "**🕙 Uptime**", value = f"∟ {uptime}", inline = True)
    embed.add_field(name = "**👨‍💻 Code**", value = f"∟ Over 3,600 lines", inline = True)
    await ctx.reply(embed = embed, mention_author = False)

  @app_commands.command(name="alert")
  async def alert(self, itx: discord.Interaction):
    """
    View alerts from the developer!
    """
    self.bot.dbo["others"]["read_alert"].append(itx.user.id)
    embed = discord.Embed(
      title = "New Alert",
      description = self.bot.dbo["others"]["alert_msg"].replace("\\n", "\n"),
      color = blurple
    )
    await itx.response.send_message(embed=embed)

    
async def setup(bot):
  await bot.add_cog(Info(bot))