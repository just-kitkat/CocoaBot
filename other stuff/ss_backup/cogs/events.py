import discord, time, asyncio, random, traceback
from vars import *
from discord.ext import commands, tasks
from errors import *

class Events(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("We have logged in as {0.user}".format(self.bot))
    
    restart_channel = self.bot.get_channel(958267420538175498)
    await restart_channel.send(f"**{bot_name}** just restarted! <t:{int(_time.time())}:R>")
    
    await self.tasksloop.start()

  @commands.Cog.listener()
  async def on_message(self, ctx):
    username = ctx.author.name
    msg = ctx.content
    channel = ctx.channel.name
    if not ctx.author.bot:
      print(f"{username}: {msg} ({ctx.guild.name} | {channel})")
      if "<@942716917821632572>" in msg or "<@!942716917821632572>" in msg:
        await ctx.reply(f"My prefix is `{self.bot.prefix}` \nThis is a test bot for Second Serving to test new features!")
      if msg.lower() == "work" and ctx.channel.id == 937479769384177664 and self.bot.active_customer:
        if str(ctx.author.id) in self.bot.db["economy"]["users"]:
          self.bot.active_customer, self.bot.db["economy"]["active_customer"] = False, False
          guild = self.bot.get_guild(936983441516396554)
          income_channel = guild.get_channel(937479769384177664)
          income = await self.bot.get_income(str(ctx.author.id))
          customer_income = random.randint(income, income * 3)
          cincome = f"{customer_income:,}"
          customer_rep = round(random.uniform(0.04, 0.25), 2)
          customer_messages = [
            f"enjoyed your dessert and tipped you **{customer_income} {coin}**", 
            f"absolutely LOVED your dessert and tipped you a generous **{customer_income} {coin}**", 
            f"gave you **{customer_income} {coin}** for that amazing customer service"
          ]
          
          title, message, color = "Customer", f"**{random.choice(celebrities)}** {random.choice(customer_messages)}! \nYou have gained **{customer_rep} {erep}**", green
          embed = discord.Embed(title = title, description = message, color = color)
          await ctx.reply(embed = embed)
          
          self.bot.db["economy"]["users"][str(ctx.author.id)]["balance"] += customer_income
          self.bot.db["economy"]["users"][str(ctx.author.id)]["rep"] += round(customer_rep, 2)
          
          
          await income_channel.set_permissions(guild.default_role, send_messages = False)
          await self.bot.save_db()
        else:
          await ctx.reply(f"You do not own a dessert shop! Use `{self.bot.prefix}build` to build one!", mention_author = False)

  @tasks.loop(seconds = 30.0, reconnect = True)
  async def tasksloop(self):
    guild = self.bot.get_guild(936983441516396554)
    await self.bot.check_blacklists()
    last_income = self.bot.db["economy"]["last_income"]
    if int(time.time()) - last_income >= 3600:
      
      income_channel = self.bot.get_channel(937479769384177664)
      logs_channel = self.bot.get_channel(955604665431621662)
      customer_rng = random.randint(1,2)
      self.bot.giving_income = True
      
      income_missed = (int(time.time()) - last_income) // 3600 # hours missed
      inactive_users = 0
      for i in range(income_missed):
        for user in self.bot.db["economy"]["users"]:
          income = await self.bot.get_income(user)
          happiness = self.bot.db["economy"]["users"][user]["happiness"]
          if happiness > 0:
            self.bot.db["economy"]["users"][user]["happiness"] -= 1
          if happiness <= 0:
            self.bot.db["economy"]["users"][user]["happiness"] = 0
            inactive_users += 1
          self.bot.db["economy"]["users"][user]["balance"] += int(income / 100 * happiness)
      
          
          for boost in self.bot.db["economy"]["users"][user]["boost"]:
            if self.bot.db["economy"]["users"][user]["boost"][boost] > 0:
              self.bot.db["economy"]["users"][user]["boost"][boost] -= 1
  #      await logs_channel.send(f"Giving income. Times: {i}")
          
      self.bot.db["economy"]["last_income"] = last_income + income_missed * 3600
      users = len(self.bot.db["economy"]["users"])
      await self.bot.save_db()
      embed = discord.Embed(
        title = f"Hourly Income",
        description = f"__**{users}**__ have received their hourly income! \n<t:{int(time.time())}:R> \nMissed: {income_missed} \nInactive users: **{inactive_users / income_missed}**"
      )
      await logs_channel.send(embed = embed)
      if customer_rng == 1 and not self.bot.active_customer:
        self.bot.active_customer = True
        self.bot.db["economy"]["active_customer"] = True
        embed = discord.Embed(
          title = "New customer",
          description = "A customer has arived and ordered some dessert. Serve him by typing `work`!",
          color = discord.Color.green()
        )
        await income_channel.send(customer_ping, embed = embed)
        await income_channel.set_permissions(guild.default_role, send_messages = True)
        await self.bot.save_db()
      self.bot.giving_income = False

  async def bot_check(self, ctx):
    if str(ctx.author.id) not in self.bot.db["economy"]["user_blacklist"]:
      if self.bot.db["economy"]["maintenance"] and ctx.author.id != 915156033192734760:
        embed = discord.Embed(
          title = bot_name,
          description = f"{bot_name} is currently in maintenance mode. \nFor more information, join the support server [here]({sinvite}).",
          color = discord.Color.red()
        )
        await ctx.reply(embed = embed)
      elif str(ctx.guild.id) in self.bot.db["economy"]["guild_config"] and ctx.channel.id in self.bot.db["economy"]["guild_config"][str(ctx.guild.id)]["blacklist"]:
        if self.bot.db["economy"]["guild_config"][str(ctx.guild.id)]["notify"]:
          embed = discord.Embed(
            title = bot_name,
            description = f"{cross} You are not allowed to use bot commands in this channel!",
            color = discord.Color.red()
          )
          msg = await ctx.reply(embed = embed)
          await asyncio.sleep(3)
          await msg.delete()
        return False
      else:
        return True
    else:
      return False

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
      return
    elif isinstance(error, commands.MissingRequiredArgument):
      return
    elif isinstance(error, KeyError):
      message = f"{cross} That user does not own a dessert shop!"
    else:
      try:
        raise error
      except Exception as e:
        error_count = self.bot.db["economy"]["error"]["error_count"]
        message = f"Oops, something went wrong while running this command! Please report this by creating a ticket in the official {bot_name} server! Thank you! \nError id: **{error_count}** \n{adv_msg}"
        channel = self.bot.get_channel(947477442786893844)
        ctx_stuff = [ctx.args, ctx.author, ctx.author.id, ctx.channel, ctx.command, ctx.guild.id, ctx.prefix, ctx.message]
        error_msg = f"```{traceback.format_exc()}\nLogs: \nMessage Info: {ctx_stuff[-1]} \n\nCommand used: {ctx.message.content}```"
    embed = discord.Embed(
        title = bot_name,
        description = message, 
        color = discord.Color.red()
      )
    
    await ctx.reply(embed = embed, mention_author = False)
    try:
      error_embed = discord.Embed(
          title = f"Error ID {error_count}",
          description = error_msg, 
          color = discord.Color.green()
        )
      await channel.send(embed = error_embed)
    except:
      return
    self.bot.db["economy"]["error"]["error_count"] += 1
    await self.bot.save_db()

  

async def setup(bot):
  await bot.add_cog(Events(bot))

