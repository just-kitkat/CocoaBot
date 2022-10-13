import discord
from vars import *
from discord import app_commands
from discord.ext import commands, tasks

class Events(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    #bot.tree.on_error = self.on_app_command_error  

  @commands.Cog.listener()
  async def on_ready(self):
    print("We have logged in as {0.user}".format(self.bot))
    await self.tasksloop.start()

  @commands.Cog.listener()
  async def on_app_command_completion(self, itx: discord.Interaction, command):
    print(f"slash after_invoke ({command})")
    await self.bot.save_db()
    if self.bot.dbo["others"]["last_income"] + 3600 > int(time.time()):
      await self.tasksloop.start()

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

  @tasks.loop(seconds = 60*60, reconnect = True) # hourly loop
  async def tasksloop(self):
    # await self.bot.wait_until_ready()
    guild = self.bot.get_guild(923013388966166528)
    #await self.bot.check_blacklists()
    last_income = self.bot.dbo["others"]["last_income"]
    if int(time.time()) - last_income >= 3600:
      income_channel = self.bot.get_channel(1030085358299385866)
      income_missed = (int(time.time()) - last_income) // 3600 # hours missed
      inactive_users = 0
      for i in range(income_missed):
        for user in self.bot.db["economy"]:
          income = await self.bot.get_income(user)
          self.bot.db["economy"][user]["balance"] += income
          
      self.bot.dbo["others"]["last_income"] = last_income + income_missed * 3600
      users = len(self.bot.db["economy"])
      await self.bot.save_db()
      embed = discord.Embed(
        title = f"Hourly Income",
        description = f"__**{users}**__ have received their hourly income! \n<t:{int(time.time())}:R> \nMissed: {income_missed}"
      )
      await income_channel.send(embed = embed)

async def setup(bot):
  await bot.add_cog(Events(bot))