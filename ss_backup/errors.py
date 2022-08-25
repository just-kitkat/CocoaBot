import discord
from discord.ext import commands

def guild_admin_check():
  def pred(ctx):
    try:
      user = ctx.author.id
      guild_name = ctx.bot.db["economy"]["users"][str(user)]["guild"]
      user_rank = ctx.bot.db["economy"]["guild"][guild_name]["members"][str(user)]["rank"]
      guild_admins = ["owner", "co owner"]
      return user_rank in guild_admins
    except: 
      return False
  return commands.check(pred)

def guild_check():
  def pred(ctx):
    try:
      user = ctx.author.id
      guild_name = ctx.bot.db["economy"]["users"][str(user)]["guild"]
      return guild_name != ""
    except: 
      return False
  return commands.check(pred)

def shop_check():
  def pred(ctx):
    if str(ctx.author.id) in ctx.bot.db["economy"]["users"]:
      return True
    raise ShopCheck(f"You do not own a dessert shop! Use `{ctx.bot.prefix}build` to build one.")
  return commands.check(pred)

class ShopCheck(commands.CheckFailure):
  pass