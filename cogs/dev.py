import discord
import os
import sys
import asyncio
from datetime import date
from vars import *
from utils import *
from errors import *
from discord import Object, app_commands
from discord.ext import commands
from importlib import reload
from typing import Optional, Literal
import importlib

class Dev(commands.Cog, command_attrs=dict(hidden=True)):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  @commands.is_owner()
  async def test(self, ctx):
    await ctx.reply("Raising an error...", mention_author = False)
    a

  @app_commands.command()
  @is_owner()
  async def slashtest(self, itx: discord.Interaction, test_arg: Optional[str]=None):
    await itx.response.send_message("Raising an error...")
    a

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
    await itx.response.send_message(f"Added **{amt} {diamond}** to **{user}**. \n**{user.name}** now has **{diamonds +  amt} {diamond}**!")

  @commands.command()
  @commands.is_owner()
  async def dropcode(self, ctx, channel : discord.TextChannel, code, amount : int):
    embed = discord.Embed(
      title = "New Code Drop!",
      description = f"A CocoaBot code has appeared! \nCode: `{code}` \nReward: **{amount} {coin}** \nClaim the code using `{self.bot.prefix}redeem <code>`", 
      color = discord.Color.blurple()
    )
    embed.set_footer(text = "The code is only valid for one person. Good luck!")
    await channel.send(embed = embed)
    self.bot.dbo["others"]["code"][code] = amount
    await ctx.reply(f"Code created!")
    channel = self.bot.get_channel(968460468505153616)
    embed = discord.Embed(title = f"A code has been created.", description = f"Code: `{code}` \nAmount: **{amount} {coin}**", color = discord.Color.green())
    await channel.send(embed = embed)
  @dropcode.error
  async def dropcode_error(self, ctx, error):
    if ctx.author.id == 915156033192734760:
      await ctx.reply(f"Please use `{self.bot.prefix}dropcode <#channel> <code> <amount>`.")
    else:
      await ctx.reply("You do not have permission to create codes!")
  
  @commands.command(name="reload")
  @commands.is_owner()
  async def _reload(self, ctx, name = None):
    others = ["errors", "vars", "utils"]
    if name is None:
      for _ in range(2): # Need to reload modules 2 times for changes to show
        message = ""
        message += "\n**Other reloaded files:** \n"
        for module in others:
          try:
            actual_module = sys.modules[module]
            importlib.reload(actual_module)
            message += f"{tick} Reloaded `{module}.py`! \n"
          except Exception as e:
            message += f"{cross} failed to reload `{module}.py` \nERROR: {e} \n"
        message += "\n**Reloaded Cogs:** \n"
        for file in os.listdir("./cogs"):
          if file.endswith(".py"):
            try:
              await self.bot.reload_extension(f"cogs.{file[:-3]}")
              message += f"{tick} Reloaded `{file}`! \n"
            except Exception as e:
              message += f"{cross} Failed to reload `{file}` \nERROR: {e} \n"
      
          
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
  async def leaveserver(self, ctx, guild_id):
      await self.bot.get_guild(int(guild_id)).leave()
      await ctx.send(f"Successfully left {guild_id}")

  @app_commands.command(name="createalert")
  @is_owner()
  async def create_alert(self, itx: discord.Interaction, alert: str):
    self.bot.dbo["others"]["alert_msg"] = alert
    self.bot.dbo["others"]["read_alert"] = []
    self.bot.dbo["others"]["alert_ping"] = True
    await itx.response.send_message(f"Alert created! \nAlert: \n{alert}")

  @commands.command(aliases=["mm"])
  @commands.is_owner()
  async def maintenancemode(self, ctx):
    self.bot.dbo["others"]["maintenancemode"] = not self.bot.dbo["others"]["maintenancemode"]
    mm = self.bot.dbo["others"]["maintenancemode"]
    await ctx.send(f"Maintenance mode set to {mm}!")

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
    elif arg1 == "task":
      events = self.bot.get_cog("events")
      try:
        await events.tasksloop()
        await ctx.send("Task has started")
      except:
        await ctx.send("Task already running")
    elif arg1 == "resetdbo":
      await ctx.send("Resetting dbo...")
      try:
        total_cmds_ran = self.bot.dbo["others"]["total_commands_ran"]
      except Exception:
        total_cmds_ran = -1
      self.bot.dbo = {
        "others":
        {
          "alert_msg": "Hello there! \nIf you see this, I probably made a mistake somewhere... (oops) \nPlease pretend this doesn't exist :)",
          "read_alert": [], # list of user IDs
          "alert_ping": False,
          "lottery": {
            "cost": 1,
            "msgid": None,
            "end": 1,
          },
          "total_commands_ran": 1057,
          "global_income_boost": {}, # {mult: duration (h)} 
          "global_xp_boost": 0, # XP BOOST NOT IMPLEMENTED
          "maintenancemode": False,
          "shop_items": {},
          "last_shop_reset": 1669564800,
          "user_blacklist": {},
          "server_blacklists": {},
          "last_income": int(time.time()) - (int(time.time()%3600)), # makes it the nearest hour
          "error_count": 1,
          "code": {}
        }
      }
      await ctx.send("DBO reset! \nTotal commands ran: " + str(total_cmds_ran))
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
          },
          "income" : {
            "times": 1,
            "times_completed": 0,
            "completed": False
          }
        }
        self.bot.db["economy"][user]["last_quest"] = 1
      await ctx.reply("updated database!")
    elif arg1 == "viewdbo":
      print(self.bot.dbo["others"])
      await ctx.send("dbo in console!")
    elif arg1 == "updatedbo":
      self.bot.dbo["others"].pop("bugs")
      await ctx.send("dbo updated!")
    elif arg1 == "updatechests":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user].pop("chests")
        self.bot.db["economy"][user]["diamonds"] = 0
    elif arg1 == "updatefish":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["fish"] = {"last_fish" : 0, "rod_level" : 1, "tuna" : 0, "grouper" : 0, "snapper" : 0, "salmon" : 0, "cod" : 0}
      await ctx.send("updated fish db")
    elif arg1 == "updatepets":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["pets"]["food"] = 0
      await ctx.send("updated pets db")
    elif arg1 == "updategames":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["games"] = {"sliding_puzzle_8_moves": -1, "sliding_puzzle_8_time": -1}
      await ctx.send("updated games db")
    elif arg1 == "updateusers":
      for user in self.bot.db["economy"]:
        for upgrade in self.bot.db["economy"][user]["upgrades"]: #farm/fact/dist
          for type_ in self.bot.db["economy"][user]["upgrades"][upgrade]: #name_of_up
            try:
              self.bot.db["economy"][user]["upgrades"][upgrade][type_].pop("coords")
              self.bot.db["economy"][user]["upgrades"][upgrade][type_].pop("cost")
              self.bot.db["economy"][user]["upgrades"][upgrade][type_].pop("income")
            except Exception as e:
              print(e)
      await ctx.send("updated users db (income)")
    elif arg1 == "resetdaily":
      if arg2 is None:
        self.bot.db["economy"][str(ctx.author.id)]["last_daily"] = int(time.time()) - 3600*24
      else:
        self.bot.db["economy"][str(ctx.author.id)]["last_daily"] = 1
      await ctx.send("Daily cooldown has been reset!")
    elif arg1 == "resetrod":
      self.bot.db["economy"][str(ctx.author.id)]["fish"]["rod_level"] = 1
      await ctx.send("rod level set to **1**")
    elif arg1 == "locreq":
      self.bot.db["economy"][str(ctx.author.id)]["levels"]["level"] = 100
      self.bot.db["economy"][str(ctx.author.id)]["balance"] = 2_500_000
      self.bot.db["economy"][str(ctx.author.id)]["golden_ticket"] += 100
      await ctx.send("Location requirements given")
    elif arg1 == "rm1boost":
      boosts = self.bot.db["economy"][str(ctx.author.id)]["boosts"]
      type_ = "income"
      for user in self.bot.db["economy"]:
        for boost in range(len(boosts[type_])): # boost = {mult: duration}
          for k in boosts[type_][boost]:
            self.bot.db["economy"][user]["boosts"][type_][boost][k] -= 1
    
            if self.bot.db["economy"][user]["boosts"][type_][boost][k] <= 0:
              self.bot.db["economy"][user]["boosts"][type_].pop(boost)
      await ctx.send("1h of income boost removed from everyone")
    elif arg1 == "rmglobal":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["boosts"].pop("global")
      await ctx.send("Global income boost removed (from user db)")
    elif arg1 == "addglobalboost":
      self.bot.dbo["others"]["global_income_boost"] = {"2": 24}
      await ctx.send("Global boost added (2x, 1d)")
    elif arg1 == "getdata":
      if arg2 is not None and arg2.isdigit():
        userdata = self.bot.db["economy"][arg2]
        with open("dump/userdata.txt", "w") as data:
          data.truncate(0)
          data.write("User Data: \n" + str(userdata) + f"\n[{int(time.time())}]")
        await ctx.send(file=discord.File("dump/userdata.txt"))
        os.remove("dump/userdata.txt")
      else:
        await ctx.send("arg2 is not a number!")
    elif arg1 == "updaterecipes":
      for user in self.bot.db["economy"]:
        self.bot.db["economy"][user]["recipes"] = {
          "fragments": {"normal": 20, "dark": 0, "milk": 0, "almond": 0, "white": 0, "caramel": 0, "peanut butter": 0, "strawberry": 0}
        }

  @app_commands.command(name="givereward")
  @is_owner()
  async def givereward(
    self, 
    itx: discord.Interaction, 
    user: discord.Member, 
    type_: Literal["balance", "diamonds", "golden_ticket"],
    amount: int
  ) -> None:
    """
    Give users a reward
    """
    rep = {
      "balance": coin,
      "diamonds": diamond,
      "golden_ticket": ticket
    }
    self.bot.db["economy"][str(user.id)][type_] += amount
    embed = discord.Embed(
      title = "Reward Given",
      description = f"**{user.name}** has been given **{amount} {rep[type_]}**!",
      color = green
    )
    await itx.response.send_message(embed=embed)



  @commands.command()
  @commands.is_owner()
  async def backup(self, ctx):
    await ctx.message.delete()
    await self.bot.create_backup()

  @commands.command()
  @commands.is_owner()
  async def blacklist(self, ctx, user : discord.Member, duration, * ,reason):
    timings = {"s": 1, "m" : 60, "h" : 3600, "d" : 86400, "w" : 604800, "mo" : 2592000, "y" : 31104000}
    time_names = {"s": "second", "m" : "minute", "h" : "hour", "d" : "day", "w" : "week", "mo" : "month", "y" : "year"}
    duration_s = int(time.time()) + int(duration[:-1]) * timings[duration[-1]]
    self.bot.dbo["others"]["user_blacklist"][str(user.id)] = {"reason" : reason, "time" : duration_s}
    title, color = bot_name, discord.Color.green()
    message = f"{tick} Successfully blacklisted **{user}** for **{duration[:-1]} {time_names[duration[-1]]}(s)**"
    embed = discord.Embed(
      title = title, color = color, 
      description = message
    )
    await ctx.reply(embed = embed, mention_author = False)
    user_embed = discord.Embed(
      title = bot_name, color = discord.Color.red(),
      description = f"You have been blacklisted from {bot_name}! \nDuration: **{duration[:-1]} {time_names[duration[-1]]}(s)** \nReason: **{reason}** \n*To appeal, join our support server [here]({disc_invite}) and create a ticket.*"
    )
    await user.send(embed = user_embed)
  
  @commands.command()
  @commands.is_owner()
  async def unblacklist(self, ctx, user : discord.Member, *, reason):
    if str(user.id) in self.bot.dbo["others"]["user_blacklist"]:
      self.bot.dbo["others"]["user_blacklist"].pop(str(user.id))
      dm_embed = discord.Embed(
        title = bot_name,
        description = f"You have been unblacklisted from {bot_name}. \nReason: **{reason}**",
        color = discord.Color.green()
      )
      embed = discord.Embed(
        title = bot_name,
        description = f"You have unblacklisted **{user}** for **{reason}**.",
        color = discord.Color.green()
      )
      await user.send(embed = dm_embed)
      await ctx.reply(embed = embed, mention_author = False)
    else:
      embed = discord.Embed(
        title = bot_name, 
        description = f"{cross} **{user}** is not blacklisted!",
        color = discord.Color.red()
      )
      await ctx.reply(embed = embed, mention_author = False)
  
  @commands.command()
  @commands.is_owner()
  async def blacklists(self, ctx):
    message, count = "", 1
    if self.bot.dbo["others"]["user_blacklist"] != {}:
      for user in self.bot.dbo["others"]["user_blacklist"]:
        username = self.bot.get_user(int(user))
        message += f"\n{count}. **{username}**"
        count += 1
    else:
      message = "No one is currently blacklisted! :D"
    embed = discord.Embed(
      title = f"{bot_name} blacklists",
      description = message,
      color = discord.Color.blue()
    )
    await ctx.reply(embed = embed, mention_author = False)
  
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

  @app_commands.command(name="lottery")
  @is_owner()
  async def lottery(self, itx: discord.Interaction, duration: str, *, price : int):
    lottery_role = "" #924492846550114365
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    lottery_time = int(duration[:-1]) * time_convert[duration
    [-1]]
    ends = int(time.time()) + lottery_time
    embed = discord.Embed(
        title="Lottery Posted!",
        description=
        f"Your lottery was posted in <#{lottery_channel}>",
        color=discord.Color.blue())
    embed.set_author(name=itx.user,
                      url=itx.user.avatar,
                      icon_url=itx.user.avatar)
    await itx.response.send_message(embed=embed)
    embed = discord.Embed(
        title=f"Lottery",
        description=
        f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{ends}:R> | <t:{ends}> \nCurrent prize pool: `No one has bought a ticket!` \nCost: {price}{coin}",
        color=discord.Color.green())
    embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
    lottery_msg = await self.bot.get_channel(lottery_channel).send(f"<@&{lottery_role}>", embed=embed)
    await lottery_msg.add_reaction("🎟️")
    self.bot.dbo["others"]["lottery"] = {
      "msgid": lottery_msg.id,
      "end": ends,
      "cost": price
    }

    
    
async def setup(bot):
  await bot.add_cog(Dev(bot))