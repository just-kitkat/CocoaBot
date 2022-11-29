import discord
import asyncio
import traceback
from vars import *
import time
from discord import app_commands
from discord.ext import commands, tasks

class Events(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    bot.tree.on_error = self.on_app_command_error  

  @commands.Cog.listener()
  async def on_ready(self):
    print("We have logged in as {0.user}".format(self.bot))
    await self.tasksloop.start()

  @commands.Cog.listener()
  async def on_app_command_completion(self, itx: discord.Interaction, command):
    print(f"slash after_invoke ({command})")
    await self.bot.save_db()
    if self.bot.dbo["others"]["last_income"] + 3600 < int(time.time()):
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

  async def on_app_command_error(self, itx: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
      message = f"{cross} You are missing the required permissions to run this command!"
    elif isinstance(error, app_commands.CommandOnCooldown):
      message = f"{cross} This command is on cooldown, you can use it in **{round(error.retry_after, 2)}s**"
    elif isinstance(error, app_commands.CheckFailure):
      message = error
      try:
        await itx.response.defer()
      except Exception:
        pass
    elif isinstance(error, KeyError):
      message = f"{cross} That user does not own a dessert shop!"
    else:
      try:
        raise error
      except Exception as e:
        error_count = self.bot.dbo["others"]["error_count"]
        message = f"Oops, something went wrong while running this command! Please report this by creating a ticket in the official {bot_name} server! Thank you! \nError id: **{error_count}** \n{adv_msg}"
        error_msg = f"""
```{traceback.format_exc()}
Logs: 
Message Info: 
- user: {itx.user}
- user id: {itx.user.id}
- channel: {itx.channel}
- guild: {itx.guild}
- guild id: {itx.guild.id}

Command used: /{itx.command.name}
Arguments: {itx.namespace}```
"""
        
    embed = discord.Embed(
        title = bot_name,
        description = message, 
        color = discord.Color.red()
      )
    await itx.channel.send(embed=embed)
    try:
      error_embed = discord.Embed(
          title = f"Error ID: {error_count}",
          description = error_msg, 
          color = discord.Color.blurple()
        )
      log_channel = self.bot.get_channel(1030104234278014976)
      await log_channel.send(embed = error_embed)
      self.bot.dbo["others"]["error_count"] += 1
      await self.bot.save_db()
    except Exception:
      return

  @commands.Cog.listener()
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
      try:
        raise error
      except Exception as e:
        error_count = self.bot.dbo["others"]["error_count"]
        message = f"Oops, something went wrong while running this command! Please report this by creating a ticket in the official {bot_name} server! Thank you! \nError id: **{error_count}** \n{adv_msg}"
        
        error_msg = f"""
```{traceback.format_exc()}
Logs: 
Message Info: 
- user: {ctx.author}
- user id: {ctx.author.id}
- channel: {ctx.channel}
- guild: {ctx.guild}
- guild id: {ctx.guild.id}

Command used: {ctx.message.content}```
"""
        
    embed = discord.Embed(
        title = bot_name,
        description = message, 
        color = discord.Color.red()
      )
    await ctx.send(embed=embed)
    try:
      error_embed = discord.Embed(
          title = f"Error ID: {error_count}",
          description = error_msg, 
          color = discord.Color.blurple()
        )
      log_channel = self.bot.get_channel(1030104234278014976)
      await log_channel.send(embed = error_embed)
      self.bot.dbo["others"]["error_count"] += 1
      await self.bot.save_db()
    except Exception:
      return

  @tasks.loop(seconds = 30, reconnect = True) # loop for hourly income
  async def tasksloop(self): # RElOADING DOES NOT UPDATE TASK LOOPS
    guild = self.bot.get_guild(923013388966166528)
    last_income = self.bot.dbo["others"]["last_income"]
    if int(time.time()) - last_income >= 3600:
      #await self.bot.check_blacklists()
      #hourly income distribution
      income_channel = self.bot.get_channel(1030085358299385866)
      income_missed = (int(time.time()) - last_income) // 3600 # hours missed
      inactive_users = 0
      msg = ""
      for i in range(income_missed):
        for user in self.bot.db["economy"]:
          income = await self.bot.get_income(user)
          income_w_cleanliness = income/100*self.bot.db["economy"][user]["cleanliness"]
          self.bot.db["economy"][user]["balance"] += income_w_cleanliness
          msg += f"{self.bot.get_user(int(user))} has recieved **{income_w_cleanliness} {coin}** ({user}) \n"
          
          #cleanliness reduction
          self.bot.db["economy"][user]["cleanliness"] -= 0.5
          if self.bot.db["economy"][user]["cleanliness"] < 0: self.bot.db["economy"][user]["cleanliness"] = 0
          
      self.bot.dbo["others"]["last_income"] = last_income + income_missed * 3600
      users = len(self.bot.db["economy"])
      embed = discord.Embed(
        title = f"Hourly Income",
        description = f"__**{users}**__ have received their hourly income! \n<t:{int(time.time())}:R> \nMissed: {income_missed - 1} \n\nUsers:\n{msg}"
      )
      await income_channel.send(embed = embed)
    await self.bot.save_db()

async def setup(bot):
  await bot.add_cog(Events(bot))