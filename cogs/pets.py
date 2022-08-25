import discord
import math, time, asyncio, random
from vars import *
from errors import *
from discord.ext import commands

class Buttons(discord.ui.View):
  def __init__(self, userID, disabled, *, timeout=120):
    self.userID = userID
    self.value = False
    super().__init__(timeout=timeout)
    self.upgrade_button.disabled = disabled
    
  @discord.ui.button(label="Upgrade", style = discord.ButtonStyle.green)
  async def upgrade_button(self, itx:discord.Interaction, button:discord.ui.Button):
    if not self.userID or itx.user.id == self.userID:
      button.disabled = True
      self.value = True
      self.stop()
      await itx.response.edit_message(view = self)
      await itx.response.defer()

class Pets(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.group(aliases = ["pet"], invoke_without_command = True)
  @factory_check()
  async def pets(self, ctx, arg = None):
    if arg is not None:
      return
    base_upgrade = 10000
    upgrades_mult = 1.7
    level = self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"]
    
    name = self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"]
    type_ = self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"]
    level = self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"]
    upgrade_cost = math.floor(base_upgrade * upgrades_mult ** level)
    if self.bot.db["economy"][str(ctx.author.id)]["prestige"] == 0 and self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] == 3:
      upgrade_cost = "Max level"
    elif self.bot.db["economy"][str(ctx.author.id)]["prestige"] == 1 and self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] == 5:
      upgrade_cost = "Max level"
    elif self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 2 and self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] == 10:
      upgrade_cost = "Max level"
    else:
      cost1 = math.floor(base_upgrade * upgrades_mult ** level)
      upgrade_cost = f"{cost1}{coin}"

    embed = discord.Embed(
      title = "Pets", 
      description= f"""You currently own a **{type_}!**
Name: **{name}**
Type: **{type_}**
Level: **{level}**
Upgrade cost: **{upgrade_cost}**
""", color = discord.Color.green())
    embed.set_footer(text = f"Do {self.bot.prefix}help pets to view more commands!")
    await ctx.reply(embed = embed, mention_author = False)

  @pets.command(aliases = ["list"])
  async def view(self, ctx):
    embed = discord.Embed(
        title = "Pets", 
        description = f"""Welcome to the pet shop! Here, you can buy many different pets! The higher level they are, the more coins you get when hunting! To buy a pet, do `{self.bot.prefix}pet buy <pet name>`. To hunt, do `{self.bot.prefix}hunt`!

**Tier 1:**
Max level: 3
Cost: 50,000{coin}
Hunt Cooldown: 1 hour

Pets available: Dog, Cat, Hamster

**Tier 2:**
Max level: 5
Cost: 100,000{coin}
Requirements: Prestige 1
Hunt Cooldown: 45 mins

Pets available: CookieMonster, Monkey, Lion, Tiger

**Tier 3:**
Max level: 10
Cost: 200,000{coin}
Requirements: Prestige 2
Hunt Cooldown: 30 mins

Pets available: Bee, Python, Seal, Eagle

**Warning:** Buying a pet will automatically abandon your previous pet and all it's levels :(
""", 
        color = discord.Color.blue()
      )
    await ctx.reply(embed = embed, mention_author = False)

  @pets.command(aliases = ["purchase", "adopt"])
  @factory_check()
  async def buy(self, ctx, pet):
    color = red
    pets = [
    None, #start list at index 1 to represent tiers system
    ["dog", "cat", "hampter"],
    ["CookieMonster", "cookiemonster", "monkey", "lion", "tiger"],
    ["bee", "python", "seal", "eagle"]
    ]
    pets_price = [None, 50000, 100000, 200000]
    
    user = ctx.author.id
    balance = self.bot.db["economy"][str(user)]["balance"]
    prestige = self.bot.db["economy"][str(user)]["prestige"]

    tier = None
    for i in pets[1:]:
      if pet in i:
        tier = pets.index(i)
        break
    if tier is None:
      msg = f"{cross} Please enter a valid pet name!"
    else:
      if prestige >= tier - 1 and balance >= pets_price[tier]:
        msg = embed = discord.Embed(
          title = f"Pet: {pet}", 
          description = f"React with a {tick} to buy a **{pet}** \n**Warning:** This purchase will abandon your previous pet (if any) and reset it's level", 
          colour = discord.Color.blurple()
            )
        pet_confirm = await ctx.send(embed = embed)

        await pet_confirm.add_reaction(tick)

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == pet_confirm and str(reaction.emoji) in [tick]
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
            if str(reaction.emoji) == tick:
                self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"] = pet
                self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"] = f"{str(ctx.author.name)}'s pet"
                self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] = 1
                self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] = tier
                self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] = 1
                self.bot.db["economy"][str(ctx.author.id)]["balance"] -= pets_price[tier]


                new_embed = discord.Embed(
                    title=f"Pet",
                    description=f"You have successfully adopted a `{pet}`! To rename it, use `{self.bot.prefix}pet name <name>`. You can use `{self.bot.prefix}hunt` to find some amazing loot!",
                    color=discord.Color.green())
                await pet_confirm.edit(embed=new_embed)

        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time!")
      else:
        if prestige < tier + 1:
          msg = f"{cross} You need to be at least **Prestige {tier + 1}** to adopt this pet!"
        else:
          msg = f"You do not have enough money to adopt this pet!"
        embed = discord.Embed(title = "Pets", description = msg, color = color)
        await ctx.reply(embed = embed, mention_author = False)

  @pets.command(aliases = ["up"])
  @factory_check()
  @pet_check()
  async def upgrade(self, ctx):
    color = red
    button_disabled = True
    base_upgrade = 10000
    upgrades_mult = 1.7
    pet_level = self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"]
    upgrade_cost = math.floor(base_upgrade * upgrades_mult ** pet_level)
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    tier = self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"]
    name = self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"]
    if tier == 1 and pet_level >= 3:
      msg = f"Your pet is tier 1 and it can only be upgraded to level 3. Do `{self.bot.prefix}pet list` to view pets in higher tier!"
    elif tier == 2 and pet_level >= 5:
      msg = f"Your pet is tier 2 and it can only be upgraded to level 5. Do `{self.bot.prefix}pet list` to view pets in higher tier!"
    elif tier == 3 and pet_level >= 10:
      msg = f"Your pet is tier 3 and it can only be upgraded to level 10. Do `{self.bot.prefix}pet list` to view pets in other tier!"
    else:
      if balance >= upgrade_cost:
        msg = f"**{name}** is level {pet_level} \nUpgrade cost: **{upgrade_cost:,} {coin}** \nBalance: **{balance:,}{coin}**"
        button_disabled = False
        color = discord.Color.blurple()
      elif balance < upgrade_cost:
        msg = f"**{name}** is level {pet_level} \nUpgrade cost: **{upgrade_cost:,}{coin}** \nBalance: **{balance:,}{coin}** \nYou do not have enough money to upgrade your pet!"
    embed = discord.Embed(title = "Pets Upgrade", description = msg, color = color)
    view = Buttons(ctx.author.id, button_disabled)
    await ctx.reply(embed = embed, mention_author = False, view = view)
    await view.wait()
    if view.value:
      self.bot.db["economy"][str(ctx.author.id)]["balance"] -= upgrade_cost
      self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] += 1
      embed = discord.Embed(title = "Pet upgraded!", description = f"**{name}** has been upgraded to **level {pet_level + 1}**", color = green)
      await ctx.reply(embed = embed, mention_author = False)

  @pets.command(alias = ["name"])
  @factory_check()
  @pet_check()
  async def rename(self, ctx, name):
    color = red
    if len(arg2) <= 16:
      if name in ("@everyone", "@here", "discord.gg"):
        msg = "Nice try but KitkatBot cannot be fooled! Try naming your pet something else!"
      else: 
        self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"] = name
        msg, color = f"You have successfully renamed your pet to `{name}`", green
    else:
      msg = "Please make sure your pet's name does not exceed 16 characters!"
    embed = discord.Embed(title = "Pets", description = msg, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @commands.command(aliases = ["h"])
  @factory_check()
  @pet_check()
  async def hunt(self, ctx):
    """Go hunting with your pet and find some amazing rewards!"""
    color = red
    name = self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"]
    level = self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"]
    amt_of_coins = math.floor(random.randint(level * 800, (level + 10) * 1000))
    if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 1:
      cooldown = 3600
      mins_ = 60
    if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 2:
      cooldown = 2700
      mins_ = 45
    if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 3:
      cooldown = 1800
      mins_ = 30
    if int(time.time()) >= self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] + cooldown:
      self.bot.db["economy"][str(ctx.author.id)]["balance"] += amt_of_coins
      self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] = time.time()
      msg, color = f"**{name}** went out hunting and brought back **{amt_of_coins}{coin}!** You can upgrade your pet using `{self.bot.prefix}pet upgrade`.", green

    elif time.time() < self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] + cooldown:
      currenttime = int(time.time())
      last_hunt = self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"]
      mins_left = str(math.floor((mins_ - ((currenttime - last_hunt) % 3600) / 60)))
      secs_left = str(math.floor((60 - ((currenttime - last_hunt) % 3600) % 60)))
      msg = f"**{name}** just went out to hunt and needs to rest! **{name}** will be ready to hunt again in `{mins_left}m {secs_left}s`"
    embed = discord.Embed(title = "Hunting", description = msg, color = color)
    if random.randint(1, 2) == 1:
      embed.set_footer(text = f"Tip: Set your pet's name using {self.bot.prefix}pet name <name>")
    await ctx.reply(embed = embed, mention_author = False)

async def setup(bot):
  await bot.add_cog(Pets(bot))