import discord, os, sys, asyncio
from datetime import date
from vars import *
from errors import *
from discord import Object, app_commands
from discord.ext import commands
from importlib import reload
from typing import Optional, Literal

class Dev(commands.Cog, command_attrs=dict(hidden=True)):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  @commands.is_owner()
  async def test(self, ctx):
    await ctx.reply("Raising an error...", mention_author = False)
    a
    await ctx.reply("No error raised? :O")

  @commands.command()
  @commands.guild_only()
  @commands.is_owner()
  async def sync(self, ctx: Object, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^", "-", "help"]] = None) -> None:
    if not guilds:
      if spec == "~":
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
      elif spec == "*":
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
      elif spec == "^":
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        synced = []
      elif spec == "-":
        ctx.bot.tree.clear_commands(guild = None)
        await ctx.bot.tree.sync()
        await ctx.send(f"Cleared all global commands")
        return
      elif spec == "help":
        await ctx.send(f"""
.sync -> global sync
.sync ~ -> sync current guild
.sync * -> copies all global app commands to current guild and syncs
.sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
.sync id_1 id_2 -> syncs guilds with id 1 and 2
.sync - -> clears all global slash commands
.sync help -> calls this help page
""")
      else:
        synced = await ctx.bot.tree.sync()

      await ctx.send(
        f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
      )
      return

    ret = 0
    for guild in guilds:
      try:
        await ctx.bot.tree.sync(guild=guild)
      except discord.HTTPException:
        pass
      else:
        ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

  @app_commands.command()
  @is_owner()
  async def addmoney(self, itx: discord.Interaction, amount: int, user: Optional[discord.Member] = None):
    if user is None: user = itx.user
    self.bot.db["economy"][str(user.id)]["balance"] += amount
    await itx.response.send_message(f"Added **{amount} {coin}** to {user.name}!")

  @app_commands.command()
  @is_owner()
  async def adddiamonds(self, itx: discord.Interaction, user:discord.Member, amt:int):
    diamonds = self.bot.db["economy"][str(user.id)]["diamonds"]
    self.bot.db["economy"][str(user.id)]["diamonds"] += amt
    await itx.response.send_message(f"Added **{amt} {diamond}** to **{user}**. **{user.name}** now has **{diamonds +  amt} {diamond}**!")

  @commands.command()
  @commands.is_owner()
  async def dropcode(self, ctx, channel : discord.TextChannel, code, amount : int):
    embed = discord.Embed(
      title = "New Code Drop!",
      description = f"A KitkatBot code has appeared! \nCode: `{code}` \nReward: **{amount} {coin}** \nClaim the code using `{self.bot.prefix}redeem <code>`", 
      color = discord.Color.blurple()
    )
    embed.set_footer(text = "The code is only valid for one person. Good luck!")
    await channel.send(embed = embed)
    self.bot.dbo["others"]["code"][code] = amount
    await ctx.reply(f"Code created!")
    channel = bot.get_guild(923013388966166528).get_channel(968460468505153616)
    embed = discord.Embed(title = f"A code has been created.", description = f"Code: `{code}` \nAmount: **{amount} {coin}**", color = discord.Color.green())
    await channel.send(embed = embed)
  @dropcode.error
  async def dropcode_error(self, ctx, error):
    if ctx.author.id == 915156033192734760:
      await ctx.reply(f"Please use `{self.bot.prefix}dropcode <#channel> <code> <amount>`.")
    else:
      await ctx.reply("You do not have permission to create codes!")
  
  @commands.command()
  @commands.is_owner()
  async def reload(self, ctx, name = None):
    others = ["errors", "vars"]
    if name is None:
      message = ""
      for file in os.listdir("./cogs"):
        if file.endswith(".py"):
          try:
            await self.bot.reload_extension(f"cogs.{file[:-3]}")
            message += f"{tick} Reloaded {file}! \n"
          except Exception as e:
            message += f"{cross} Failed to reload {file} \nERROR: {e} \n"
    elif f"{name}.py" in os.listdir("./cogs"):
      await self.bot.reload_extension(f"cogs.{name}")
      message = f"{tick} Cog reloaded!"
      
    else:
      message = f"{cross} Cog not found!"

    embed = discord.Embed(title = "Developer Tools", description = message, color = discord.Color.blurple())
    await ctx.reply(embed = embed, mention_author = False)

  @commands.command()
  @commands.is_owner()
  async def load(self, ctx, name = None):
    if name is None:
      message = "Please specify cog to load!"
    else:
      file = name + ".py"
      try:
        await self.bot.load_extension(f"cogs.{name}")
        message = f"{tick} Loaded {file}! \n"
      except Exception as e:
        message = f"{cross} Failed to load {file} \nERROR: {e} \n"
    embed = discord.Embed(title = "Developer Tools", description = message, color = discord.Color.blurple())
    await ctx.reply(embed = embed, mention_author = False)
        
  @commands.command()
  @commands.is_owner()
  async def unload(self, ctx, name = None):
    if name is None:
      message = "Please specify cog to unload!"
    else:
      file = name + ".py"
      try:
        await self.bot.unload_extension(f"cogs.{file[:-3]}")
        message = f"{tick} Unloaded {file}! \n"
      except Exception as e:
        message = f"{cross} Failed to unload {file} \nERROR: {e} \n"
    embed = discord.Embed(title = "Developer Tools", description = message, color = discord.Color.blurple())
    await ctx.reply(embed = embed, mention_author = False)


  @commands.command()
  @commands.is_owner()
  async def dev(self, ctx, arg1 = None, arg2 = None):
    if arg1 is None:
      pass
    elif arg1 == "kill":
      msg = await ctx.send("Stopping all processes...")
      #await update_status(True)
      await msg.edit(content=f"Killing {bot_name}...")
      await self.bot.close()
    elif arg1 == "restart":
      await ctx.send("Restarting bot... `This might take a few seconds`")
      os.execv(sys.executable, ['python'] + sys.argv)
    elif arg1 == "updatequest":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["quest"] = {
          "fish" : {
            "name": "tuna",
            "times": 5,
            "completed": False
          },
          "hunt" : {
            "times": 1,
            "times_completed": 0,
            "completed": False
          }
        }
        self.bot.db["economy"][user]["last_quest"] = 1
      await ctx.reply("updated database!")
    elif arg1 == "updatechests":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user].pop("chests")
        self.bot.db["economy"][user]["diamonds"] = 0
    elif arg1 == "updatefish":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["fish"] = {"last_fish" : 0, "rod_level" : 1, "tuna" : 0, "grouper" : 0, "snapper" : 0, "salmon" : 0, "cod" : 0}
      await ctx.send("updated fish db")



  @commands.command()
  @commands.is_owner()
  async def backup(self, ctx):
    data = self.bot.db["economy"]
    today = date.today()
    timestamp = today.strftime("%d %B %Y, %A")
    with open("backup.txt", "w") as backup:
        backup.truncate(0)
        data = db["economy"]
        data2 = dbo["others"]
        backup.write("Economy: \n" + str(data) + "\nOthers: \n" + str(data2) + f"\n[{int(time.time())}]")
        await ctx.send(file=discord.File("backup.txt"))
        os.remove("backup.txt")
    await ctx.message.delete()
    await ctx.send(file=discord.File("backup.txt"))
    os.remove("backup.txt")
  
  @commands.command()
  @commands.is_owner()
  async def leaveserver(self, ctx, guild_id):
    if ctx.author.id == 915156033192734760:
      await self.bot.get_guild(int(guild_id)).leave()
      await ctx.send(f"Successfully left {guild_id}")
  
  @commands.command()
  @commands.is_owner()
  async def reseteconomy(self, ctx, member: discord.Member = None):
    if member is None:
      embed = discord.Embed(
          title=f"Economy Reset",
          description=
          f"React with a ✅ to reset the economy! \n**Warning**: This cannot be undone",
          color=discord.Color.red())
      msg = await ctx.send(embed=embed)
      await msg.add_reaction("✅")
  
      def check(reaction, user):
        return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
  
      try:
        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "✅":
            self.bot.db["economy"] = {}
            new_embed = discord.Embed(
              title=f"Economy Reset",
              description=f"The economy has been successfully resetted!",
              color=discord.Color.green())
            await msg.edit(embed=new_embed)
  
      except asyncio.TimeoutError:
          await ctx.reply("You did not react in time.")
    else:
      embed = discord.Embed(
          title=f"Economy Reset",
          description=
          f"React with a ✅ to reset the economy for {member.mention}! \n**Warning**: This cannot be undone",
          color=discord.Color.red())
      msg = await ctx.send(embed=embed)
      await msg.add_reaction("✅")
      def check(reaction, user):
        return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
      try:
        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "✅":
          self.bot.db["economy"].pop(str(member.id)) 
          new_embed = discord.Embed(
            title=f"Economy Reset",
            description=f"The economy has been successfully resetted for {member.mention}!",
            color=discord.Color.green())
          await msg.edit(embed=new_embed)
  
      except asyncio.TimeoutError:
          await ctx.reply("You did not react in time.")

  @commands.command()
  async def lottery(self, ctx, duration=None, *, price : int=None):
    if ctx.author.id == 915156033192734760:
      lottery_channel = 923121739637088256 #924492712328171530
      lottery_role = "" #924492846550114365
      if duration is None:
          return await ctx.send(
              f"Please enter a time and a prize! (`{self.bot.prefix}lottery <time> <prize> | s = seconds, m = minutes, h = hours, d = days`)"
          )
      elif price is None:
          await ctx.send(f"Please enter a prize! (`{self.bot.prefix}gcreate <time> <prize>`)")
  
      time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
      lottery_time = int(duration[:-1]) * time_convert[duration
      [-1]]
      ends = int(time.time()) + lottery_time
      embed = discord.Embed(
          title="Lottery Posted!",
          description=
          f"Your lottery was posted in <#{lottery_channel}>",
          color=discord.Color.blue())
      embed.set_author(name=ctx.message.author,
                        url=ctx.author.avatar,
                        icon_url=ctx.author.avatar)
      await ctx.send(embed=embed)
      embed = discord.Embed(
          title=f"Lottery",
          description=
          f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{ends}:R> | <t:{ends}> \nCurrent prize pool: `No one has bought a ticket!` \nCost: {price}{coin}",
          color=discord.Color.green())
      embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
      lottery_msg = await ctx.guild.get_channel(lottery_channel).send(f"<@&{lottery_role}>", embed=embed)
      await lottery_msg.add_reaction("🎟️")
  
      count = 0
      while count < lottery_time:
        count += 60
        users = 0
        channel_posted = ctx.guild.get_channel(lottery_channel)
        new_lottery_msg = await channel_posted.fetch_message(lottery_msg.id)
        user_list = [
          u async for u in new_lottery_msg.reactions[0].users()
          if u != self.bot.user
        ]
        user_list_copy = user_list.copy()
        for i in user_list_copy:
          if self.bot.db["economy"][str(i.id)]["balance"] >= price:
            users += 1
            user_list.remove(i)
        if users <= 1:
          new_embed = discord.Embed(
          title=f"Lottery",
          description=
          f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{ends}:R> | <t:{ends}> \nCurrent prize pool: `Not enough tickets purchased!` \nCost: {price}{coin} \nNumber of tickets bought: `{users}`",
          color=discord.Color.green())
          new_embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
        else:
          new_embed = discord.Embed(
          title=f"Lottery",
          description=
          f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{ends}:R> | <t:{ends}> \nCurrent prize pool: **{users * price}{coin}** \nCost: **{price}{coin}** \nNumber of tickets bought: `{users}`",
          color=discord.Color.green())
          new_embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
        
        await new_lottery_msg.edit(embed = new_embed)
        await asyncio.sleep(60)
  
      channel_posted = ctx.guild.get_channel(lottery_channel)
      new_lottery_msg = await channel_posted.fetch_message(lottery_msg.id)
      user_list = [u async for u in new_lottery_msg.reactions[0].users() if u != self.bot.user]
      user_list_copy = user_list.copy()
      for i in user_list_copy:
        if self.bot.db["economy"][str(i.id)]["balance"] <= price:
          user_list.remove(i)
      if len(user_list) <= 1:
          await lottery_msg.reply("Not enough people joined the lottery.")
      else:
          winner = random.choice(user_list)
          for user in user_list:
            self.bot.db["economy"][str(user.id)]["balance"] -= price
          prize = len(user_list) * price
          await lottery_msg.reply(f"{winner.mention} has won **{prize}{coin}**! (Tickets purchased: {len(user_list)})")
          self.bot.db["economy"][str(winner.id)]["balance"] += prize
          channel_posted = ctx.guild.get_channel(lottery_channel)
          new_lottery_msg = await channel_posted.fetch_message(lottery_msg.id)
          final_embed = discord.Embed(
          title=f"Lottery",
          description=
          f"The lottery ended <t:{ends}:R> | <t:{ends}>! \nPrize pool: **{users * price}{coin}** \nWinner: `{winner}` \nNumber of tickets bought: `{users}`",
          color=discord.Color.green())
          await new_lottery_msg.edit(embed = final_embed)
  """
  @commands.command(aliases = ["mm"])
  @commands.is_owner()
  async def maintenancemode(self, ctx):
    maintenance = self.bot.db["economy"]["maintenance"]
    self.bot.db["economy"]["maintenance"] = not maintenance
    embed = discord.Embed(
      title = bot_name,
      description = f"Set bot's maintenance to **{not maintenance}**!",
      color = discord.Color.green()
    )
    await ctx.reply(embed = embed)"""
    
async def setup(bot):
  await bot.add_cog(Dev(bot))