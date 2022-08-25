import discord
from skimage import color
from skimage import io
import random, time
from vars import *
from errors import *
from discord.ext import commands

class Buttons(discord.ui.View):
  def __init__(self, userID, *, timeout=120):
    self.userID = userID
    self.value = False
    super().__init__(timeout=timeout)

  @discord.ui.button(label = trashcan, style = discord.ButtonStyle.red)
  async def delete_msg(self, itx:discord.Interaction, button:discord.ui.Button):
    if itx.user.id == self.userID:
      self.value = True
      self.stop()
      await itx.response.defer()

class Fun(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases = ["monochrome"])
  @commands.cooldown(1, 5, commands.BucketType.user)
  async def mono(self, ctx, user : discord.Member=None):
    """Converts a user's avatar into black and white"""
    processing_start = time.time()
    if user is None:
      user = ctx.author
    try:
      await user.avatar.save("images/mono.jpg")
      img = io.imread('images/mono.jpg')[:,:,:3]
      imgGray = io.imsave("images/mono.jpg", color.rgb2gray(img))
      file = discord.File("images/mono.jpg")
      processing_time = round((time.time() - processing_start) * 1000, 2)
      msg = f"Processing Time: {processing_time}ms"
      embed = discord.Embed(title = "Image to Monochrome", description = msg, color = green)
      
      file = discord.File("images/mono.jpg", filename="temp.jpg")
      embed.set_image(url="attachment://temp.jpg")
      view = Buttons(ctx.author.id)
      message = await ctx.reply(file=file, embed=embed, view = view, mention_author = False)
      await view.wait()
      if view.value:
        await message.delete()
        await ctx.message.delete()

    except AttributeError as e:
      embed = discord.Embed(title = "Image to Monochrome", description = f"This user does not have a custom avatar set! \nERROR: {e}", color = red)
      await ctx.reply(embed = embed, mention_author = False)
    

"""  @commands.command()
  async def lego(self, ctx, user : discord.Member=None):
    "Replaces the pixels in the image with lego bricks"
    async with ctx.processing():
      file, embed = await imaging.lego(image or await ImageConverter._convert(ctx))  # type: ignore
      await ctx.reply(file=file, embed=embed)"""

async def setup(bot):
  await bot.add_cog(Fun(bot))