import discord
from skimage import color
from skimage import io
import random, time
from vars import *
from errors import *
from discord import app_commands
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

class Fun(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name = "monochrome")
  @commands.cooldown(1, 5, commands.BucketType.user)
  async def monochrome(self, itx: discord.Interaction, user : discord.Member=None):
    """Converts a user's avatar into black and white"""
    processing_start = time.time()
    if user is None:
      user = itx.user
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
      view = Buttons(itx.user.id)
      await itx.response.send_message(file=file, embed=embed, view = view)
      await view.wait()
      if view.value:
        await itx.delete_original_response()

    except AttributeError as e:
      embed = discord.Embed(title = "Image to Monochrome", description = f"This user does not have a custom avatar set!", color = red)
      await itx.response.send_message(embed = embed, ephemeral = True)
    

"""  @commands.command()
  async def lego(self, ctx, user : discord.Member=None):
    "Replaces the pixels in the image with lego bricks"
    async with ctx.processing():
      file, embed = await imaging.lego(image or await ImageConverter._convert(ctx))  # type: ignore
      await ctx.reply(file=file, embed=embed)"""

async def setup(bot):
  await bot.add_cog(Fun(bot))