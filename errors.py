import discord
from discord.ext import commands

def factory_check():
  def pred(ctx):
    if str(ctx.author.id) in ctx.bot.db["economy"]:
      return True
    raise FactoryCheck(f"{cross} You do not own a kitkat factory! Use `{ctx.bot.prefix}start` to build one.")
  return commands.check(pred)

class FactoryCheck(commands.CheckFailure):
  pass

def pet_check():
  def pred(ctx):
    if str(ctx.author.id) in ctx.bot.db["economy"] and ctx.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] > 0:
      return True
    raise PetCheck(f"{cross} You do not own a pet! Use `{ctx.bot.prefix}pets` to adopt one.")
  return commands.check(pred)

class PetCheck(commands.CheckFailure):
  pass