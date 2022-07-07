import discord, os, sys
from vars import *
from discord.ext import commands

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
  @commands.is_owner()
  async def addmoney(self, ctx, user : discord.Member, amount : int):
    guild = bot.get_guild(936983441516396554)
  #  tester_role = guild.get_role(937349187673141308)
    if user != ctx.author and ctx.author.id != 915156033192734760:
      await ctx.reply("You can only mention yourself!", mention_author = False)
      return
    self.bot.db["economy"]["users"][str(user.id)]["balance"] += amount
    await ctx.reply(f"Added **{amount} {coin}** to {user.name}!", mention_author = False)
      
  @addmoney.error
  async def addmoney_error(self, ctx, error):
    await ctx.reply(f"Please use `{self.bot.prefix}addmoney <user> <amount>`", mention_author = False)
  
  @commands.command()
  @commands.is_owner()
  async def reload(self, ctx, name = None):
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

    await self.bot.emby(ctx, "Developer Tools", message, discord.Color.blurple())

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
    await self.bot.emby(ctx, "Developer Tools", message, discord.Color.blurple())
        
  @commands.command()
  @commands.is_owner()
  async def unload(self, ctx, name = None):
    if name is None:
      message = "Please specify cog to unload!"
    else:
      file = name + ".py"
      try:
        async with self.bot:
          await self.bot.unload_extension(f"cogs.{file[:-3]}")
          message = f"{tick} Unloaded {file}! \n"
      except Exception as e:
        message = f"{cross} Failed to unload {file} \nERROR: {e} \n"
    await self.bot.emby(ctx, "Developer Tools", message, discord.Color.blurple())


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


  @commands.command()
  @commands.is_owner()
  async def blacklist(self, ctx, user : discord.Member, duration, * ,reason):
    timings = {"m" : 60, "h" : 3600, "d" : 86400, "w" : 604800, "mo" : 2592000, "y" : 31104000}
    time_names = {"m" : "minute", "h" : "hour", "d" : "day", "w" : "week", "mo" : "month", "y" : "year"}
    duration_s = int(time.time()) + int(duration[:-1]) * timings[duration[-1]]
    self.bot.db["economy"]["user_blacklist"][str(user.id)] = {"reason" : reason, "time" : duration_s}
    title, color = bot_name, discord.Color.green()
    message = f"{tick} Successfully blacklisted **{user}** for **{duration[:-1]} {time_names[duration[-1]]}(s)**"
    embed = discord.Embed(
      title = title, color = color, 
      description = message
    )
    await ctx.reply(embed = embed, mention_author = False)
    user_embed = discord.Embed(
      title = bot_name, color = discord.Color.red(),
      description = f"You have been blacklisted from {bot_name}! \nDuration: **{duration[:-1]} {time_names[duration[-1]]}(s)** \nReason: **{reason}** \n*To appeal, join our support server [here]({sinvite}) and create a ticket.*"
    )
    await user.send(embed = user_embed)
  
  @commands.command()
  @commands.is_owner()
  async def unblacklist(self, ctx, user : discord.Member, *, reason):
    if str(user.id) in self.bot.db["economy"]["user_blacklist"]:
      self.bot.db["economy"]["user_blacklist"].pop(str(user.id))
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
    if self.bot.db["economy"]["user_blacklist"] != {}:
      for user in self.bot.db["economy"]["user_blacklist"]:
        username = bot.get_user(int(user))
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
  async def backup(self, ctx):
    data = self.bot.db["economy"]
    today = date.today()
    timestamp = today.strftime("%d %B %Y, %A")
    with open("backup.txt", "w") as backup:
      backup.truncate(0)
      backup.write(str(data) + f"\n{timestamp} [{int(time.time())}]")
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
        return user == ctx.author and str(reaction.emoji) in ["✅"]
  
      try:
        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "✅":
            self.bot.db["economy"]["users"] = {}
            self.bot.db["economy"]["guild"] = {}
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
        return user == ctx.author and str(reaction.emoji) in ["✅"]
      try:
        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "✅":
          guild = self.bot.db["economy"]["users"][str(member.id)]["guild"]
          self.bot.db["economy"]["users"].pop(str(member.id))
          if guild != "":
            rank = self.bot.db["economy"]["guild"][guild]["owner"]
            if str(member.id) == rank:
              self.bot.db["economy"]["guild"].pop(guild)
            else:
              self.bot.db["economy"]["guild"][guild]["members"].pop(str(member.id))
          new_embed = discord.Embed(
            title=f"Economy Reset",
            description=f"The economy has been successfully resetted for {member.mention}!",
            color=discord.Color.green())
          await msg.edit(embed=new_embed)
  
      except asyncio.TimeoutError:
          await ctx.reply("You did not react in time.")
  
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
    await ctx.reply(embed = embed)
    
async def setup(bot):
  await bot.add_cog(Dev(bot))