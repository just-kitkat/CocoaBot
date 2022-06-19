import discord, time, asyncio, random
from vars import *
from discord.ext import commands, tasks

class Events(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("We have logged in as {0.user}".format(self.bot))
    
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

  @tasks.loop(seconds = 30.0, reconnect = True)
  async def tasksloop(self):
    guild = self.bot.get_guild(936983441516396554)
    
    last_income = self.bot.db["economy"]["last_income"]
    if int(time.time()) - last_income >= 3600:
      await self.bot.check_blacklists()
      
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


async def setup(bot):
  await bot.add_cog(Events(bot))

