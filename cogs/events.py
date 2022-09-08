import discord
from vars import *
from discord import app_commands
from discord.ext import commands

class Events(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    #bot.tree.on_error = self.on_app_command_error  

  @commands.Cog.listener()
  async def on_ready(self):
    print("We have logged in as {0.user}".format(self.bot))

  @commands.Cog.listener()
  async def on_app_command_completion(self, itx: discord.Interaction, command):
    print(f"slash after_invoke ({command})")
    await self.bot.save_db()

  @commands.Cog.listener()
  async def on_message(self, ctx):
    username = ctx.author.name
    msg = ctx.content
    try:
      channel = ctx.channel.name
    except:
      channel = "DM CHANNEL"
    if not ctx.author.bot:
      print(f"{username}: {msg} ({ctx.guild.name} | {channel})")

  async def on_app_command_error_(self, itx: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
      message = f"{cross} You are missing the required permissions to run this command!"
    elif isinstance(error, app_commands.CommandOnCooldown):
      message = f"{cross} This command is on cooldown, you can use it in **{round(error.retry_after, 2)}s**"
    elif isinstance(error, app_commands.CheckFailure):
      message = error
    elif isinstance(error, KeyError):
      message = f"{cross} That user does not own a dessert shop!"
    else:
      message = str(error)
      message += "\nPlease report this to kitkat3141"
    embed = discord.Embed(title = "An error occured", description = message, color = red)
    try:
      await itx.response.send_message(embed = embed)
    except Exception as e:
      print("EH error:", e)
      await itx.channel.send(embed = embed)

  #@commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
      message = f"{cross} You are missing the required permissions to run this command!"
    elif isinstance(error, commands.CommandOnCooldown):
      message = f"{cross} This command is on cooldown, you can use it in **{round(error.retry_after, 2)}s**"
    elif isinstance(error, commands.CheckFailure):
      message = error
    elif isinstance(error, commands.MemberNotFound):
      message = f"{cross} User not found! Please try using the user's ID or mention them!"
    elif isinstance(error, commands.MissingRequiredArgument):
      message = error
    elif isinstance(error, KeyError):
      message = f"{cross} That user does not own a dessert shop!"
    else:
      message = str(error)
      message += "\nPlease report this to kitkat3141"
    embed = discord.Embed(title = "An error occured", description = message, color = red)
    await ctx.reply(embed = embed, mention_author = False)
  

async def setup(bot):
  await bot.add_cog(Events(bot))