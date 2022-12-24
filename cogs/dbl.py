from discord.ext import commands
import os
import topgg


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
    channel = self.bot.get_channel(923013388966166532)
    user = self.bot.get_user(int(data["user"]))
    if user is None: user = "Someone"
    await channel.send(f"{user} upvoted CocoaBot! Thank you! :D")

  @commands.Cog.listener()
  async def on_dbl_test(self, data):
    """
    An event that is called whenever someone tests the webhook system for your bot on top.gg.
    """
    print("Received a test upvote:", "\n", data)


async def setup(bot):
  await bot.add_cog(TopGG(bot))