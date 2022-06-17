import discord
from vars import *
from discord.ext import commands

class Admin(commands.Cog, name = "Admin Commands"):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def prefix(self, ctx, arg = None, new_prefix = None):
    title, color = bot_name, discord.Color.red()
    if arg is None or arg != "edit":
      title, color = bot_name, discord.Color.green()
      message = f"My prefix is `{self.bot.prefix}` \nTo change it, use `{self.bot.prefix}prefix edit <new prefix>`."
    elif arg == "edit":
      if new_prefix is None:
        message = f"{cross} Please use `{self.bot.prefix}prefix edit <new prefix>`"
      elif len(new_prefix) < 5:
        if ctx.message.author.guild_permissions.administrator:
          self.bot.db["economy"]["prefix"][str(ctx.guild.id)] = new_prefix
          color = discord.Color.green()
          message = f"{tick} Bot's prefix successfully changed to `{new_prefix}`"
        else:
          message = f"{cross} You need the **Administrator** permission to change the bot's prefix!"
      else:
        message = f"{cross} Please make sure the bot's prefix is less than 5 letters!"
    embed = discord.Embed(
      title = title,
      description = message,
      color = color
    )
    await ctx.reply(embed = embed, mention_author = False)

  # Server Configs
  @commands.command(aliases = ["config", "conf"])
  async def configuration(self, ctx, arg = None, arg2 = None, arg3 = None):
    if ctx.message.author.guild_permissions.manage_guild:
      gid = str(ctx.guild.id)
      if gid not in self.bot.db["economy"]["guild_config"]:
        self.bot.db["economy"]["guild_config"][str(ctx.guild.id)] = {"blacklist" : [], "notify" : True}
      conf = self.bot.db["economy"]["guild_config"][gid]
      if arg is None:
        title, message, color = "Server Configuration", f"""
  Server Prefix: `{self.bot.prefix}` 
  Blacklist channels: `{self.bot.prefix}conf blacklist <#channel>` 
  Blacklist Notification: `{self.bot.prefix}conf blacklist notify`
  View Blacklisted Channels: `{self.bot.prefix}conf blacklist list`
  Remove All Channels From Blacklist: `{self.bot.prefix}conf blacklist clear`
  """, green
  
      elif arg == "blacklist":
        if arg2 is None:
          title, message, color = "Channel Blacklist", f"{cross} Please mention a channel! `{self.bot.prefix}conf blacklist <#channel>`.", red
        elif arg2 == "notify":
          self.bot.db["economy"]["guild_config"][gid]["notify"] = not conf["notify"]
          notify = conf["notify"]
          title, message, color = "Blacklist Notification", f"Blacklist notifications set to **{notify}**", green
        elif arg2 == "list":
          title, color, message = "Blacklisted Channels", green, ""
          count = 1
          for channel in self.bot.db["economy"]["guild_config"][gid]["blacklist"]:
            # Checks if that channel still exists
            validity_test = self.bot.get_guild(int(gid)).get_channel(channel)
            if validity_test == None:
              self.bot.db["economy"]["guild_config"][gid]["blacklist"].remove(channel)
              continue
            message += f"{count}. <#{channel}> [ID: {channel}] \n"
            count += 1
          if message == "":
            message = f"You do not have any channels blacklisted! Use `{self.bot.prefix}conf blacklist <#channel>` to blacklist channels!"
        elif arg2 == "clear":
          title, message, color = "Server Configuraion", f"All channels have been removed from the blacklist!", green
          self.bot.db["economy"]["guild_config"][gid]["blacklist"] = []
        else:
          arg2 = arg2.replace("#", "").replace("<", "").replace(">", "")
          try:
            channel = self.bot.get_guild(int(gid)).get_channel(int(arg2))
            if int(arg2) not in conf["blacklist"] and arg2 != None: 
              self.bot.db["economy"]["guild_config"][gid]["blacklist"].append(int(arg2))
              title, message, color = "Channel Blacklist", f"{tick} <#{channel.id}> has been blacklisted. Users will not be able to use commands in that channel anymore!", green
            elif arg2 != None:
              self.bot.db["economy"]["guild_config"][str(ctx.guild.id)]["blacklist"].remove(int(arg2))
              title, message, color = "Channel Blacklist", f"{tick} <#{channel.id}> has been removed from the blacklist. Users will now be able to use commands in that channel again!", green
            else:
              title, message, color = "Channel Blacklist", f"{cross} Invalid channel! Please use `{self.bot.prefix}conf blacklist <#channel>`", red
          except:
            title, message, color = "Channel Blacklist", f"{cross} Invalid channel! Please use `{self.bot.prefix}conf blacklist <#channel>`", red
      
      else:
        title, message, color = "Server Configuration", f"{cross} Argument not recognised! Please use `{self.bot.prefix}conf` for more information.", red
  
      
    else:
      title, message, color = "Server Configuration", f"{cross} You need the **Manage Server** permission to edit your server configuraton!", red
    embed = discord.Embed(title = title, description = message, color = color)
    await ctx.reply(embed = embed, mention_author = False)

def setup(bot):
  bot.add_cog(Admin(bot))