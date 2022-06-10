import discord, os
from vars import *
from discord.ext import commands

class Dev(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def reload(self, ctx, name = None):
    if name is None:
      message = ""
      for file in os.listdir("./cogs"):
        if file.endswith(".py"):
          try:
            self.bot.reload_extension(f"cogs.{file[:-3]}")
            message += f"{tick} Loaded {file}! \n"
          except Exception as e:
            messgae += f"{cross} Failed to load {file} \nERROR: {e} \n"

    elif f"{name}.py" in os.listdir("./cogs"):
        self.bot.reload_extension(f"cogs.{name}")
        message = f"{tick} Cog reloaded!"
      
    else:
      message = f"{cross} Cog not found!"

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

    
def setup(bot):
  bot.add_cog(Dev(bot))