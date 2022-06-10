import discord, time
from vars import *
from discord.ext import commands

class Info(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ping(self, ctx):
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


def setup(bot):
  bot.add_cog(Info(bot))