import discord
from vars import *
from discord import app_commands

def factory_check():
  """
  Checks if users have an account (a farm)
  """
  def pred(itx: discord.Interaction):
    if str(itx.user.id) in itx.client.db["economy"]:
      return True
    raise FactoryCheck(f"{cross} You do not own a chocolate farm! Use `{itx.client.prefix}start` to build one.")
  return app_commands.check(pred)

class FactoryCheck(app_commands.CheckFailure):
  pass

def pet_check():
  """
  Check if users own pets
  """
  def pred(itx: discord.Interaction):
    if str(itx.user.id) in itx.client.db["economy"] and itx.client.db["economy"][str(itx.user.id)]["pets"]["tier"] > 0:
      return True
    raise PetCheck(f"{cross} You do not own a pet! Use `{itx.client.prefix}pets list` to view available pets!")
  return app_commands.check(pred)

class PetCheck(app_commands.CheckFailure):
  pass

def is_owner():
  """
  Check if user is the owner 
  """
  def pred(itx: discord.Interaction):
    if itx.user.id == 915156033192734760:
      return True
    raise OwnerCheck(f"{cross} You do not have access to this command!")
  return app_commands.check(pred)

class OwnerCheck(app_commands.CheckFailure):
  pass


def has_voted():
  """
  Check if user has voted for the bot
  """
  def pred(itx: discord.Interaction):
    if itx.client.db["economy"][str(itx.user.id)]["vote"]["last_vote"] + 3600*24 >= int(time.time()):
      return True
    raise VoteCheck(f"{cross} You need to vote for me on top.gg in the last 24 hours before using this command! \nUse `{prefix}vote` to vote for me!")
  return app_commands.check(pred)

class VoteCheck(app_commands.CheckFailure):
  pass