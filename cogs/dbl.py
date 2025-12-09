from discord.ext import commands
import discord
from vars import *
import os
import topgg
import time


class TopGG(commands.Cog):
  """
  Handles bot votes relating to top.gg
  """
  def __init__(self, bot):
    self.bot = bot
    #self.bot.token = os.getenv("TOPGG_TOKEN")
    self.bot.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook("/dblwebhook", os.getenv("DBLHOOK_PASS"))
    self.bot.topgg_webhook.run(5000)
    
  @commands.Cog.listener()
  async def on_dbl_vote(self, data):
    """
    An event that is called whenever someone votes for the bot on top.gg.
    """
    if data["type"] == "test":
      # this is roughly equivalent to
      # return await on_dbl_test(data) in this case
      return self.bot.dispatch('dbl_test', data)
      
    print("Received an upvote:", "\n", data)
    try:
      channel = self.bot.get_channel(923013388966166532) # announce vote to #general
      user = self.bot.get_user(int(data["user"]))
      if user is None: user = "Someone"
      # Remove vote message from #general. will be added back if chat becomes more active
      # await channel.send(f"{user} upvoted CocoaBot! Thank you! :D")
      await self.bot.log_action("Vote", f"{user} voted for CocoaBot!")
    except Exception as err:
      print(f"Failed to get vote info: {err}")
    
    if str(user.id) in self.bot.db["economy"]:
      if self.bot.db["economy"][str(user.id)]["vote"]["last_vote"] + 3600*24*3 >= int(time.time()):
        self.bot.db["economy"][str(user.id)]["vote"]["streak"] += 1
      else:
        self.bot.db["economy"][str(user.id)]["vote"]["streak"] = 1
        
      self.bot.db["economy"][str(user.id)]["vote"]["last_vote"] = int(time.time())
      self.bot.db["economy"][str(user.id)]["vote"]["count"] += 1
      streak = self.bot.db["economy"][str(user.id)]["vote"]["streak"]
      
      rewards = {
        "diamonds": 10,
        "ticket": 1*(streak//7 + 1) if streak%7==0 else 1 # give extra tickets every 7 days of streak
      }
      
      self.bot.db["economy"][str(user.id)]["golden_ticket"] += rewards["ticket"]
      self.bot.db["economy"][str(user.id)]["diamonds"] += rewards["diamonds"]
      
      dm = False
      try:
        await user.send(embed=discord.Embed(
          title = "Thanks for voting!",
          description = f"""
We really appreciate the vote! Here are some goodies for you.
{rewards['ticket']}x {ticket}
{rewards['diamonds']}x {diamond}

Daily Streak: {streak}
Get extra goodies every 7 vote streak!

*Vote again in 12 hours to get more goodies!*
""",
          color = blurple
        ))
        dm = True
      except Exception as e:
        dm = f"False, {e}"
          
      await self.bot.log_action("Vote rewards", f"{user} recieved their vote rewards! \nDM status: {dm}")
        
    

  @commands.Cog.listener()
  async def on_dbl_test(self, data):
    """
    An event that is called whenever someone tests the webhook system for your bot on top.gg.
    """
    print("Received a test upvote:", "\n", data)


async def setup(bot):
  await bot.add_cog(TopGG(bot))