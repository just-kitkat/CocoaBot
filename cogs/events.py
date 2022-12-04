import discord
import asyncio
import traceback
import random
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
    if not self.bot.cache["logged_restart"]:
      embed = discord.Embed(
        title=f"{bot_name} Restart", 
        description=f"{bot_name} restarted <t:{int(time.time())}:R> \nPing: `{round(self.bot.latency*1000, 1)}ms`", 
        color=blurple
      )
      await self.bot.get_channel(restart_log_channel).send(embed=embed)
      self.bot.cache["logged_restart"] = True

    await self.tasksloop.start()

  @commands.Cog.listener()
  async def on_app_command_completion(self, itx: discord.Interaction, command):
    print(f"slash after_invoke ({command.name})")
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
    old_cmds = ["?s", "?d", "?h", "?s", "?w", "?m", "?start", "?lb"]
    if msg in old_cmds:
      await ctx.reply("Hello! I have migrated to slash commands! Please use `/tutorial` for available commands.")

  async def on_app_command_error(self, itx: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
      message = f"{cross} You are missing the required permissions to run this command!"
    elif isinstance(error, app_commands.CommandOnCooldown):
      message = f"{cross} This command is on cooldown, you can use it in **{round(error.retry_after, 2)}s**"
    elif isinstance(error, app_commands.CheckFailure):
      message = error
      try:
        await itx.response.defer(thinking=False)
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

    if self.bot.dbo["others"]["lottery"]["msgid"] is not None:
      users = 0
      lottery_msg = self.bot.dbo["others"]["lottery"]["msgid"]
      end = self.bot.dbo["others"]["lottery"]["end"]
      price = self.bot.dbo["others"]["lottery"]["cost"]
      channel_posted = self.bot.get_channel(lottery_channel)
      lottery_msg = await channel_posted.fetch_message(lottery_msg)
      user_list = [
        u async for u in lottery_msg.reactions[0].users()
        if u != self.bot.user
      ]
      user_list_copy = user_list.copy()
      for i in user_list_copy:
        if self.bot.db["economy"][str(i.id)]["balance"] >= price:
          users += 1
          user_list.remove(i)
      if int(time.time()) < self.bot.dbo["others"]["lottery"]["end"]:
        if users <= 1:
          new_embed = discord.Embed(
          title=f"Lottery",
          description=
          f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{end}:R> | <t:{end}> \nCurrent prize pool: `Not enough tickets purchased!` \nCost: {price}{coin} \nNumber of tickets bought: `{users}`",
          color=discord.Color.green())
          new_embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
        else:
          new_embed = discord.Embed(
          title=f"Lottery",
          description=
          f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{end}:R> | <t:{end}> \nCurrent prize pool: **{users * price}{coin}** \nCost: **{price}{coin}** \nNumber of tickets bought: `{users}`",
          color=discord.Color.green())
          new_embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
        
        await lottery_msg.edit(embed = new_embed)
      else:
        if users <= 1:
          await lottery_msg.reply("Not enough people joined the lottery.")
        else:
          user_list = user_list_copy
          winner = random.choice(user_list)
          for user in user_list:
            self.bot.db["economy"][str(user.id)]["balance"] -= price
          prize = len(user_list) * price
          await lottery_msg.reply(f"{winner.mention} has won **{prize}{coin}**! (Tickets purchased: {len(user_list)})")
          self.bot.db["economy"][str(winner.id)]["balance"] += prize
          channel_posted = self.bot.get_channel(lottery_channel)
          final_embed = discord.Embed(
          title=f"Lottery",
          description=
          f"The lottery ended <t:{end}:R> | <t:{end}>! \nPrize pool: **{users * price}{coin}** \nWinner: `{winner}` \nNumber of tickets bought: `{users}`",
          color=discord.Color.green())
          await lottery_msg.edit(embed = final_embed)
        self.bot.dbo["others"]["lottery"] = {
          "msgid": None,
          "end": 1,
          "cost": 1
        }
    
    last_income = self.bot.dbo["others"]["last_income"]
    if int(time.time()) - last_income >= 3600:
      #await self.bot.check_blacklists()
      #hourly income distribution
      income_channel = self.bot.get_channel(1030085358299385866)
      income_missed = (int(time.time()) - last_income) // 3600 # hours missed
      inactive_users = 0
      for i in range(income_missed):
        msg = ""
        for user in self.bot.db["economy"]:
          income, mult = await self.bot.get_income(user)
          income_w_cleanliness = round(income/100*self.bot.db["economy"][user]["cleanliness"])
          self.bot.db["economy"][user]["balance"] += income_w_cleanliness
          
          #cleanliness reduction
          self.bot.db["economy"][user]["cleanliness"] -= 0.5
          if self.bot.db["economy"][user]["cleanliness"] < 0: 
            self.bot.db["economy"][user]["cleanliness"] = 0

          msg += f"{self.bot.get_user(int(user))} has recieved **{income_w_cleanliness} {coin}** \nMults (i,g,p): {mult} \n(cleanliness: {self.bot.db['economy'][user]['cleanliness']}%, id: {user}) \n"

          # boost reduction
          boosts = self.bot.db["economy"][user]["boosts"]
          type_ = "income"
          for boost in range(len(boosts[type_])): # boost = {mult: duration}
            for k in boosts[type_][boost]:
              self.bot.db["economy"][user]["boosts"][type_][boost][k] -= 1

              if self.bot.db["economy"][user]["boosts"][type_][boost][k] <= 0:
                self.bot.db["economy"][user]["boosts"][type_].pop(boost)
          for k in self.bot.dbo["others"]["global_income_boost"]:
            self.bot.dbo["others"]["global_income_boost"][k] -= 1
            if self.bot.dbo["others"]["global_income_boost"][k] <= 0:
              self.bot.dbo["others"]["global_income_boost"] = {}
      boosts = self.bot.db["economy"][user]["boosts"]
      type_ = "xp"
      for boost in range(len(boosts[type_])): # boost = {mult: duration}
        for k in boosts[type_][boost]:
          self.bot.db["economy"][user]["boosts"][type_][boost][k] -= 1

          if self.bot.db["economy"][user]["boosts"][type_][boost][k] <= 0:
            self.bot.db["economy"][user]["boosts"][type_].pop(boost)
      """ this is for global xp boost reduction, which has not been implemented yet!
      for k in self.bot.dbo["others"]["global_income_boost"]:
        self.bot.dbo["others"]["global_income_boost"][k] -= 1
        if self.bot.dbo["others"]["global_income_boost"][k] <= 0:
          self.bot.dbo["others"]["global_income_boost"] = {}
      """
      self.bot.dbo["others"]["last_income"] = last_income + income_missed * 3600
      users = len(self.bot.db["economy"])
      try:
        embed = discord.Embed(
          title = f"Hourly Income",
          description = f"__**{users}**__ have received their hourly income! \n<t:{int(time.time())}:R> \nMissed: {income_missed - 1} \n\nUsers:\n{msg}"
        )
        await income_channel.send(embed = embed)
      except Exception as e:
        embed = discord.Embed(
          title = f"Hourly Income",
          description = f"__**{users}**__ have received their hourly income! \n<t:{int(time.time())}:R> \nMissed: {income_missed - 1} \nLOG FAILED, ERROR: {E}"
        )
        await income_channel.send(embed = embed)

    # Handle shop resets (daily)
    last_shop_reset = self.bot.dbo["others"]["last_shop_reset"]
    if int(time.time()) - last_shop_reset >= 3600*24:
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["bought_from_shop"] = []

      possibilities = list(shop_info["tickets"])
      items = random.sample(possibilities, 3)
      self.bot.dbo["others"]["shop_items"] = {
        item: random.randint(
          shop_info["tickets"][item] - 3, 
          shop_info["tickets"][item] + 3
        ) for item in items
      } # item: price
      resets_missed = (int(time.time()) - last_shop_reset) // (3600*24)
      self.bot.dbo["others"]["last_shop_reset"] = last_shop_reset + resets_missed*3600*24
    await self.bot.save_db()

async def setup(bot):
  await bot.add_cog(Events(bot))