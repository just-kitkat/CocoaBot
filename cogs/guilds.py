import discord
from vars import *
from discord.ext import commands
color = green

class Guilds(commands.Cog, name = "Guild Commands"):

  def __init__(self, bot):
    self.bot = bot

  def admin_check():
    def predicate(ctx):
      try:
        user = ctx.author.id
        guild_name = ctx.bot.db["economy"]["users"][str(user)]["guild"]
        user_rank = ctx.bot.db["economy"]["guild"][guild_name]["members"][str(user)]["rank"]
        guild_admins = ["owner", "co owner"]
        return user_rank in guild_admins
      except: 
        return False
    return commands.check(predicate)

  def shop_check():
    def predicate(ctx):
      return str(ctx.author.id) in ctx.bot.db["economy"]["users"]
    return commands.check(predicate)

  @commands.group(aliases = ["g", "guilds"], invoke_without_command = True)
  @shop_check()
  async def guild(self, ctx):
    "`.g help` for guild related commands"
    if str(ctx.author.id) in self.bot.db["economy"]["users"]:
      user = ctx.author.id 
      title = "Guilds"
      color = green
      balance = self.bot.db["economy"]["users"][str(user)]["balance"]
      income = await self.bot.get_income(user)
  
      guild_income_req = 20000
      guild_bal_req = 1000000
      color = discord.Color.red()
      if self.bot.db["economy"]["users"][str(user)]["guild"] != "":
        guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
        guild_members = len(self.bot.db["economy"]["guild"][guild_name]["members"])
        guild_level = self.bot.db["economy"]["guild"][guild_name]["level"]
        guild_xp = self.bot.db["economy"]["guild"][guild_name]["xp"]
        guild_xpneeded = self.bot.db["economy"]["guild"][guild_name]["xp_needed"]
        rank = self.bot.db["economy"]["guild"][guild_name]["members"][str(user)]["rank"]
        guild_xp_mult = self.bot.db["economy"]["guild"][guild_name]["xp_mult"]
        user_donate = self.bot.db["economy"]["guild"][guild_name]["members"][str(user)]["donate"]
        guild_tag = self.bot.db["economy"]["guild"][guild_name]["tag"]
        if guild_tag == "": 
          guild_tag_format = f"No tag set! `{self.bot.prefix}g tag <tag>`" 
        else:
          guild_tag_format = f"**{guild_tag}**"
        color = discord.Color.green()
        
        guild_bal = 0
        for i in self.bot.db["economy"]["guild"][guild_name]["members"]:
          guild_bal += self.bot.db["economy"]["guild"][guild_name]["members"][i]["donate"]
          
        emoji = ""
        xp_emoji = "🟩"
        no_xp_emoji = "⬛"
        levels = int(guild_xp/guild_xpneeded * 10)
        for i in range(0, levels):
          emoji += xp_emoji
        for i in range(0, 10 - levels):
          emoji += no_xp_emoji
        message = f"""
Guild: **{guild_name}** | `{guild_members}` members
Rank: {rank.title()}
Tag: {guild_tag_format}
Guild Balance: **{guild_bal:,} {coin}**
Xp Multiplier: **{guild_xp_mult}x**
        
Level: **{guild_level}** \n{emoji} `({guild_xp} / {guild_xpneeded})`
*Use `{self.bot.prefix}help guild` to view guild commands!*
"""
      else:
        message = f"You are not in a guild! *Use `{self.bot.prefix}help guild` to view guild commands.*"
    else:
      title, message, color = bot_name, f"{cross} You do not own a dessert shop. Use `{self.bot.prefix}build` to build one!",discord.Color.red()
    
    embed = discord.Embed(
      title = title,
      description = message,
      color = color
    )
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  async def create(self, ctx, name = None, *, space = None):
    "Create a guild using `guild create [name]`"
    user = ctx.author.id
    if self.bot.db["economy"]["users"][str(user)]["guild"] == "":
      if income >= guild_income_req and balance >= guild_bal_req:
        if name is not None and len(name) < 15 and space is None:
          guild_list = []
          for guild in self.bot.db["economy"]["guild"]:
            guild_list.append(guild.lower())
          if name.lower() not in guild_list:
            self.bot.db["economy"]["guild"][name] = {"level" : 0, "balance" : 0, "tag" : "", "invites" : [], "members" :{str(user) : {"rank" : "owner", "donate" : 0}}, "income_mult" : 2, "owner" : str(user), "xp" : 0, "xp_needed" : 100, "xp_mult" : 1}
            
            self.bot.db["economy"]["users"][str(user)]["guild"] = name
            self.bot.db["economy"]["users"][str(user)]["balance"] -= guild_bal_req
            title = "Guild created!"
            message, color = f"{tick} You have created a guild! Invite your friends using `{self.bot.prefix}g invite <user>`!", green
            await self.bot.log_action(ctx, "guild", f"**{ctx.author}** ({ctx.author.id}) has created a guild called **{name}**")
          else:
            color = red
            message = f"{cross} This guild already exists! Please choose another name!"
        elif name is None:
          color = red
          message = f"{cross} Please use `{self.bot.prefix}g create <name>` to create a guild!"
        elif len(name) > 15:
          color = red
          message = f"{cross} Make sure your guild name is not longer than 14 characters!"
        elif space is not None:
          color = red
          message = f"{cross} Make sure your guild name has no spaces!"
      else:
        color = red
        message = f"{cross} You need an income of **{guild_income_req} {coin}** and a balance of **{guild_bal_req} {coin}** to create a guild!"
    else:
      message, color = f"{cross} You are already in a guild!", red
    embed = discord.Embed(title = "Guilds", description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  async def join(self, ctx, name = None):
    "Join a guild!"
    user, color = ctx.author.id, green
    if self.bot.db["economy"]["users"][str(user)]["guild"] == "":
      if name is not None and name in self.bot.db["economy"]["guild"] and str(user) in self.bot.db["economy"]["guild"][name]["invites"]:
        message = f"{tick} You have successfully joined **{name}**!"
        self.bot.db["economy"]["guild"][name]["invites"].remove(str(user))
        self.bot.db["economy"]["guild"][name]["members"][str(user)] = {"rank" : "member", "donate" : 0}
        self.bot.db["economy"]["users"][str(user)]["guild"] = name
        notify_msg = f"**{ctx.author}** just joined your guild! "
        await self.bot.notify_user(ctx, int(self.bot.db["economy"]["guild"][name]["owner"]), "green", notify_msg)
        await self.bot.log_action(ctx, "guild", f"**{ctx.author}** ({ctx.author.id}) has joined **{name}**")
      elif name not in self.bot.db["economy"]["guild"]:
        message, color = f"{cross} That guild does not exist! Make sure you have typed in the name correctly! (Guild names are case-sensitive!)", red
      elif str(user) not in self.bot.db["economy"]["guild"][name]["invites"]:
        message, color = f"{cross} You do not have an invite to join **{name}**", red
      elif name is None:
        message, color = f"{cross} Please use `{self.bot.prefix}g join <guild name>`", red
      
    else:
      message, color = f"You are already in a guild! *Use `{self.bot.prefix}g leave` to leave your guild!*", red
    embed = discord.Embed(title = "Guilds", description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  # Admin commands
  @guild.command()
  @admin_check()
  async def invite(self, ctx, member : discord.Member = None):
    user, color = ctx.author.id, green
    guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
    guild_members = len(self.bot.db["economy"]["guild"][guild_name]["members"])
    invites = self.bot.db["economy"]["guild"][guild_name]["invites"]
    guild_level = self.bot.db["economy"]["guild"][guild_name]["level"]
    if member is not None and str(member.id) not in self.bot.db["economy"]["users"]:
      message, color = f"{cross} That user does not own a shop!", red
    elif member is not None and str(member.id) not in invites and user != member.id and self.bot.db["economy"]["users"][str(member.id)]["guild"] == "":
      self.bot.db["economy"]["guild"][guild_name]["invites"].append(str(member.id))
      message = f"{tick} You have successfully invited **{member.name}** to join **{guild_name}**! They have been notified and can join using `{self.bot.prefix}g join <guild name>`"
      notify_message = f"You have been invited by **{ctx.author.name}** to join a guild! \nGuild name: **{guild_name}** \nGuild Members: **{guild_members}** \nGuild level: **{guild_level}** \nUse `{self.bot.prefix}guild join {guild_name}` to join the guild!"
      await self.bot.notify_user(ctx, member.id, "green", notify_message)
      await self.bot.log_action(ctx, "guild", f"**{ctx.author}** has invited {member} ({member.id}) to join **{guild_name}**")
    elif member is None:
      message, color = f"{cross} Please use `{self.bot.prefix}g invite <user>`!", red
    elif str(member.id) in invites:
      message, color = f"{cross} **{member.name}** has already been invited to your guild!", red
    elif user == member.id:
      message, color = f"{cross} You cannot invite yourself!", red
    elif self.bot.db["economy"]["users"][str(member.id)]["guild"] != "":
      message, color = f"{cross} That user is already in a guild!", red
    embed = discord.Embed(title = "Guild Invite", description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  @admin_check()
  async def uninvite(self, ctx, member : discord.Member = None):
    user, color = ctx.author.id, green
    guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
    guild_members = len(self.bot.db["economy"]["guild"][guild_name]["members"])
    invites = self.bot.db["economy"]["guild"][guild_name]["invites"]
    guild_level = self.bot.db["economy"]["guild"][guild_name]["level"]
    if str(member.id) in self.bot.db["economy"]["users"]:
      if is_user and user_rank in guild_admins and str(member.id) in invites:
        self.bot.db["economy"]["guild"][guild_name]["invites"].remove(str(member.id))
        message = f"{tick} **{member.name}** has been removed from the guild's invite list!"
      elif user_rank not in guild_admins:
        message, color = f"{cross} You are not a guild admin!", red
      elif str(member.id) not in invites:
        message, color = f"{cross} **{member.name}** has already been invited to your guild!", red
      else:
        message, color = f"{cross} Please use `{self.bot.prefix}g uninvite <user>`!", red
    else:
      message, color = f"{cross} That user does not own a shop!", red
    embed = discord.Embed(title = "Guild Invite", description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  @admin_check()
  async def kick(self, ctx, member : discord.Member = None, *, reason = None):
    user, color = ctx.author.id, green
    guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
    if member is not None:
      if user != member.id and str(member.id) in self.bot.db["economy"]["guild"][guild_name]["members"]:
        if reason is None:
          message, color = f"{cross} You must provide a reason! Please use `{self.bot.prefix}g kick <user> <reason>`", red
        else:
          self.bot.db["economy"]["guild"][guild_name]["members"].pop(str(member.id))
          self.bot.db["economy"]["users"][str(member.id)]["guild"] = ""
          message = f"{tick} **{member.name}** has been kicked from your guild!"
          await self.bot.notify_user(ctx, member.id, "red", f"You have been kicked from **{guild_name}**. \nReason: **{reason}**")
          await self.bot.log_action(ctx, "guild", f"**{ctx.author}** ({ctx.author.id}) has kicked {member} ({member.id}) from **{guild_name}**")
      elif user == member.id:
        message, color = f"{cross} You turn around and gave yourself a hard kick. Hope that makes you happy.", red
      elif str(member.id) not in self.bot.db["economy"]["guild"][guild_name]["members"]:
        message, color = f"{cross} That user is not in your guild!", red
    else:
      message, color = f"{cross} Please use `{self.bot.prefix}g kick <user> <reason>`", red
    embed = discord.Embed(title = "Guild Kick", description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  @admin_check()
  async def tag(self, ctx, tag = None):
    user = ctx.author.id
    guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
    guild_tag = self.bot.db["economy"]["guild"][guild_name]["tag"]
    guild_members = len(self.bot.db["economy"]["guild"][guild_name]["members"])
    guild_level = self.bot.db["economy"]["guild"][guild_name]["level"]
    title, color = "Guild Tag", red
    if guild_level >= 3:
      if tag is None:
        if guild_tag == "":
          message = f"{cross} Oops, looks like you do not have a guild tag... Use `{self.bot.prefix}g tag <tag>` to create one!"
        else:
          message, color = f"Your current guild tag is **{guild_tag}**. Use `{self.bot.prefix}g tag <tag>` to change it!", green

      else:
        if tag == "remove":
          self.bot.db["economy"]["guild"][guild_name]["tag"] = ""
          message, color = f"{tick} Your guild tag has been removed!", green
        elif len(tag) == 4:
          valid = True
          for char in list(tag):
            if not (char.isalpha() or char.isnumeric()):
              message = f"{cross} The guild tag can only contain letters and numbers!"
              valid = False
              break
          if valid:
            tag = tag.upper()
            for guild in self.bot.db["economy"]["guild"]:
              if self.bot.db["economy"]["guild"][guild]["tag"] == tag:
                message = f"{cross} That tag already exists! Try using a different tag!"
                valid = False
                break
          if valid:
            self.bot.db["economy"]["guild"][guild_name]["tag"] = tag
            message, color = f"{tick} Your guild tag has been set to **{tag}**!", green
              
        else:
          message = f"{cross} Your tag must be 4 characters long!"
    else:
      message = f"{cross} Your guild needs to be level 3 to unlock a guild tag!"
    embed = discord.Embed(title = "Guild Tag", description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  async def list(self, ctx):
    user = ctx.author.id
    members = ""
    color = green
    guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
    guild_members = len(self.bot.db["economy"]["guild"][guild_name]["members"])
    for i in self.bot.db["economy"]["guild"][guild_name]["members"]:
      if self.bot.db["economy"]["guild"][guild_name]["members"][i]["rank"] != "owner":
        members += f"{self.bot.get_user(int(i)).mention} \n"
      else:
        owner = self.bot.get_user(int(i)).mention
    title, message = guild_name, f"Guild members: {guild_members} \n**Owner:** \n**{owner}** \n**Members:** \n{members}"
    embed = discord.Embed(title = title, description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  async def leave(self, ctx):
    user = ctx.author.id
    guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
    user_rank = self.bot.db["economy"]["guild"][guild_name]["members"][str(user)]["rank"]
    if user_rank != "owner":
      self.bot.db["economy"]["guild"][guild_name]["members"].pop(str(user))
      self.bot.db["economy"]["users"][str(user)]["guild"] = ""
      message, color = f"{tick} You successfully left **{guild_name}**.", green
      await self.bot.notify_user(ctx, self.bot.db["economy"]["guild"][guild_name]["owner"], red, f"**{self.bot.get_user(user)}** has left your guild.")
      await self.bot.log_action(ctx, "guild", f"**{ctx.author}** ({ctx.author.id}) has left **{guild_name}**")
    else:
      message, color = f"{cross} You are the owner of **{guild_name}** and cannot leave it! To disband your guild, use `{self.bot.prefix}g disband`.", red
    embed = discord.Embed(title = guild_name, description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @guild.command()
  async def donate(self, ctx, amount = None):
    user = ctx.author.id
    guild_name = self.bot.db["economy"]["users"][str(user)]["guild"]
    balance = self.bot.db["economy"]["users"][str(user)]["balance"]
    try:
      amount = int(amount)
      if amount > balance:
        message, color = f"{cross} Debt is not an option! Current balance: **{balance} {coin}**", red
      elif amount < 1:
        message, color = f"{cross} Are you trying to trick the system? Please donate an amount more than 0!", red
      else:
        self.bot.db["economy"]["guild"][guild_name]["members"][str(user)]["donate"] += amount
        message, color = f"You have donated **{amount} {coin}** to the guild! Use `{self.bot.prefix}g shop` to view the shop!", green
    except:
      message, color = f"Please use `{self.bot.prefix}g donate <amount>`", red
    embed = discord.Embed(title = "Guild Donation", description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

def setup(bot):
  bot.add_cog(Guilds(bot))