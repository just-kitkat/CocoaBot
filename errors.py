import discord
from vars import *
from discord import app_commands

def factory_check():
  def pred(itx: discord.Interaction):
    if str(itx.user.id) in itx.client.db["economy"]:
      return True
    raise FactoryCheck(f"{cross} You do not own a kitkat factory! Use `{itx.client.prefix}start` to build one.")
  return app_commands.check(pred)

class FactoryCheck(app_commands.CheckFailure):
  pass

def pet_check():
  def pred(itx: discord.Interaction):
    if str(itx.user.id) in itx.client.db["economy"] and itx.client.db["economy"][str(itx.user.id)]["pets"]["tier"] > 0:
      return True
    raise PetCheck(f"{cross} You do not own a pet! Use `{itx.client.prefix}pets list` to view available pets!")
  return app_commands.check(pred)

class PetCheck(app_commands.CheckFailure):
  pass

def is_owner():
  def pred(itx: discord.Interaction):
    if itx.user.id == 915156033192734760:
      return True
    raise OwnerCheck(f"{cross} You do not have access to this command!")
  return app_commands.check(pred)

class OwnerCheck(app_commands.CheckFailure):
  pass