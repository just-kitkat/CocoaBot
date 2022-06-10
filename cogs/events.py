import discord, time
from vars import *
from discord.ext import commands

class Events(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("We have logged in as {0.user}".format(self.bot))

  @commands.Cog.listener()
  async def on_message(self, ctx):
    username = ctx.author.name
    msg = ctx.content
    channel = ctx.channel.name
    if not ctx.author.bot:
      print(f"{username}: {msg} ({ctx.guild.name} | {channel})")
      if "<@942716917821632572>" in msg or "<@!942716917821632572>" in msg:
        await ctx.reply(f"My prefix is `{prefix}` \nThis is a test bot for Second Serving to test new features!")


  @commands.check
  async def check_commands(self, ctx):
    channels = [947474270991310891, 937221627622592593]
    if ctx.channel.id in channels:
      return True
    else:
      return False

  @commands.command()
  async def test(self, ctx):
    await ctx.reply("Hi!", mention_author = False)
  
  @commands.after_invoke
  async def after_invoke(self, ctx):
    print("d")
    await bot.save_db()
    print("a")

def setup(bot):
  bot.add_cog(Events(bot))