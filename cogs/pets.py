import discord
import math, time, asyncio, random
from vars import *
from errors import *
from typing import Optional, Literal
from discord import app_commands
from discord.ext import commands

class AdoptButton(discord.ui.View):
  def __init__(self, userID, *, timeout=120):
    self.userID = userID
    self.value = False
    super().__init__(timeout=timeout)
    
  @discord.ui.button(label="Adopt!", style = discord.ButtonStyle.green)
  async def adopt_button(self, itx:discord.Interaction, button:discord.ui.Button):
    button.disabled = True
    self.value = True
    await itx.response.edit_message(view = self)
    self.stop()

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

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

class Pets(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  pet = app_commands.Group(name = "pets", description = "Pet commands")

  @pet.command(name = "view")
  @factory_check()
  @pet_check()
  async def view(self, itx: discord.Interaction):
    """View your pet's information"""
    base_upgrade = 10000
    upgrades_mult = 1.7
    level = self.bot.db["economy"][str(itx.user.id)]["pets"]["level"]
    
    name = self.bot.db["economy"][str(itx.user.id)]["pets"]["name"]
    type_ = self.bot.db["economy"][str(itx.user.id)]["pets"]["type"]
    level = self.bot.db["economy"][str(itx.user.id)]["pets"]["level"]
    food = itx.client.db["economy"][str(itx.user.id)]["pets"]["food"]
    upgrade_cost = math.floor(base_upgrade * upgrades_mult ** level)
    if self.bot.db["economy"][str(itx.user.id)]["prestige"] == 0 and self.bot.db["economy"][str(itx.user.id)]["pets"]["level"] == 3:
      upgrade_cost = "Max level"
    elif self.bot.db["economy"][str(itx.user.id)]["prestige"] == 1 and self.bot.db["economy"][str(itx.user.id)]["pets"]["level"] == 5:
      upgrade_cost = "Max level"
    elif self.bot.db["economy"][str(itx.user.id)]["prestige"] >= 2 and self.bot.db["economy"][str(itx.user.id)]["pets"]["level"] == 10:
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
Happiness: **{self.bot.get_happiness(itx)}**
Pet food: **{food} pet food**
Upgrade cost: **{upgrade_cost}**
""", color = discord.Color.green())
    embed.set_footer(text = f"Do {self.bot.prefix}help pets to view more commands!")
    await itx.response.send_message(embed = embed)

  @is_owner()
  @pet.command(name = "list")
  async def list(self, itx: discord.Interaction):
    """A list of all pets up for adoption :D"""
    embed = discord.Embed(
        title = "Pets", 
        description = f"""Welcome to the pet shop! Here, you can buy many different pets! The higher level they are, the more coins you get when hunting! To buy a pet, do `{self.bot.prefix}pet adopt <pet name>`. To hunt, do `{self.bot.prefix}hunt`!

**Tier 1:**
Max level: 3
Cost: 50,000{coin}
Requirements: Prestige 1
Hunt Cooldown: 1 hour

Pets available: Dog, Cat, Hamster

**Tier 2:**
Max level: 5
Cost: 100,000{coin}
Requirements: Prestige 2
Hunt Cooldown: 45 mins

Pets available: CookieMonster, Monkey, Lion, Tiger

**Tier 3:**
Max level: 10
Cost: 200,000{coin}
Requirements: Prestige 3
Hunt Cooldown: 30 mins

Pets available: Bee, Python, Seal, Eagle

**Warning:** Buying a pet will automatically abandon your previous pet and all it's levels :(
""", 
        color = discord.Color.blue()
      )
    await itx.response.send_message(embed = embed)

  @pet.command(name = "adopt")
  @factory_check()
  @is_owner()
  async def adopt(self, itx: discord.Interaction, pet: Literal["dog", "cat", "hampter", "CookieMonster", "monkey", "lion", "tiger", "bee", "python", "seal", "eagle"]):
    """Adopt your very own pet!"""
    color = red
    pets = [
    None, #start list at index 1 to represent tiers system
    ["dog", "cat", "hampter"],
    ["CookieMonster", "cookiemonster", "monkey", "lion", "tiger"],
    ["bee", "python", "seal", "eagle"]
    ]
    pets_price = [None, 50000, 100000, 200000]
    
    user = itx.user.id
    balance = self.bot.db["economy"][str(user)]["balance"]
    prestige = self.bot.db["economy"][str(user)]["prestige"]
    
    for i in pets[1:]:
      if pet in i:
        tier = pets.index(i)
        break
        
    if prestige >= tier and balance >= pets_price[tier]:
      msg = embed = discord.Embed(
        title = f"Pet: {pet}", 
        description = f"React with a {tick} to buy a **{pet}** \n**Warning:** This purchase will abandon your previous pet (if any) and reset it's level", 
        colour = discord.Color.blurple()
          )
      view = AdoptButton(itx.user.id)
      await itx.response.send_message(embed = embed, view = view)
      await view.wait()
      if view.value:
        self.bot.db["economy"][str(itx.user.id)]["pets"]["type"] = pet
        self.bot.db["economy"][str(itx.user.id)]["pets"]["name"] = f"{str(itx.user.name)}'s pet"
        self.bot.db["economy"][str(itx.user.id)]["pets"]["last_hunt"] = 1
        self.bot.db["economy"][str(itx.user.id)]["pets"]["last_feed"] = int(time.time())
        self.bot.db["economy"][str(itx.user.id)]["pets"]["last_play"] = 1
        self.bot.db["economy"][str(itx.user.id)]["pets"]["tier"] = tier
        self.bot.db["economy"][str(itx.user.id)]["pets"]["level"] = 1
        self.bot.db["economy"][str(itx.user.id)]["balance"] -= pets_price[tier]


        new_embed = discord.Embed(
            title=f"Pet",
            description=f"You have successfully adopted a `{pet}`! \nTo rename it, use `{self.bot.prefix}pet name <name>`. You can use `{self.bot.prefix}hunt` to find some amazing loot! \nRemember to feed it everyday or it might starve!",
            color=discord.Color.green())
        await itx.edit_original_response(embed=new_embed)

      else:
        await itx.followup.send("You did not react in time!")
    else:
      if prestige < tier:
        msg = f"{cross} You need to be at least **Prestige {tier}** to adopt this pet!"
      else:
        msg = f"You do not have enough money to adopt this pet!"
      embed = discord.Embed(title = "Pets", description = msg, color = color)
      await itx.response.send_message(embed = embed)

  @pet.command(name = "upgrade")
  @factory_check()
  @pet_check()
  async def upgrade(self, itx: discord.Interaction):
    """Level up your pet for awesome perks!"""
    color = red
    button_disabled = True
    base_upgrade = 10000
    upgrades_mult = 1.7
    pet_level = self.bot.db["economy"][str(itx.user.id)]["pets"]["level"]
    upgrade_cost = math.floor(base_upgrade * upgrades_mult ** pet_level)
    balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
    tier = self.bot.db["economy"][str(itx.user.id)]["pets"]["tier"]
    name = self.bot.db["economy"][str(itx.user.id)]["pets"]["name"]
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
    view = Buttons(itx.user.id, button_disabled)
    await itx.response.send_message(embed = embed, view = view)
    await view.wait()
    if view.value:
      self.bot.db["economy"][str(itx.user.id)]["balance"] -= upgrade_cost
      self.bot.db["economy"][str(itx.user.id)]["pets"]["level"] += 1
      embed = discord.Embed(title = "Pet upgraded!", description = f"**{name}** has been upgraded to **level {pet_level + 1}**", color = green)
      await itx.edit_original_response(embed = embed)

  @pet.command(name = "play")
  @factory_check()
  @pet_check()
  async def play(self, itx: discord.Interaction):
    """Play with your pet and keep it happy!"""
    last_play = itx.client.db["economy"][str(itx.user.id)]["pets"]["last_play"]
    if int(time.time()) >= last_play + 3600:
      itx.client.db["economy"][str(itx.user.id)]["pets"]["last_play"] = int(time.time())
      name = itx.client.db["economy"][str(itx.user.id)]["pets"]["name"]
      embed = discord.Embed(title = "Pets", description = f"You played with **{name}**!", color = green)
    else:
      embed = discord.Embed(title = "Pets", description = f"Your pet is tired and need to rest! \nYou cannot play with your pet more than once every hour.", color = red)
    await itx.response.send_message(embed = embed)

  @pet.command(name = "feed")
  @factory_check()
  @pet_check()
  async def feed(self, itx: discord.Interaction):
    """Feed your pet to keep it happy and healthy!"""
    color = red
    food = itx.client.db["economy"][str(itx.user.id)]["pets"]["food"]
    if food > 0:
      if self.bot.get_happiness(itx) == 100:
        msg = f"Your pet is already full! Don't overfeed it!"
      else:
        itx.client.db["economy"][str(itx.user.id)]["pets"]["food"] -= 1
        itx.client.db["economy"][str(itx.user.id)]["pets"]["last_feed"] = int(time.time())
        msg = f"You fed your pet **1 pet food**!"
        color = green
    else:
      msg = f"You do not have any food to feed your pet! \nYou can obtain pet food by completing games and quests!"

    embed = discord.Embed(title = "Pets", description = msg, color = color)
    await itx.response.send_message(embed = embed)
    

  @pet.command(name = "rename")
  @factory_check()
  @pet_check()
  async def rename(self, itx: discord.Interaction, name: app_commands.Range[str, 1, 16]):
    """Give your pet a name!"""
    color = red
    if name in ("@everyone", "@here", "discord.gg"):
      msg = "Nice try but KitkatBot cannot be fooled! Try naming your pet something else!"
    else: 
      self.bot.db["economy"][str(itx.user.id)]["pets"]["name"] = name
      msg, color = f"You have successfully renamed your pet to `{name}`", green
    embed = discord.Embed(title = "Pets", description = msg, color = color)
    await itx.response.send_message(embed = embed)

  @app_commands.command(name = "hunt")
  @factory_check()
  @pet_check()
  async def hunt(self, itx: discord.Interaction):
    """Go hunting with your pet and find some amazing rewards!"""
    color = red
    quest_msg = get_quest_rewards(itx, "hunt")
    happiness = self.bot.get_happiness(itx)
    name = self.bot.db["economy"][str(itx.user.id)]["pets"]["name"]
    level = self.bot.db["economy"][str(itx.user.id)]["pets"]["level"]
    amt_of_coins = math.floor(random.randint(level * 800, (level + 10) * 1000))//100*happiness
    tier = self.bot.db["economy"][str(itx.user.id)]["pets"]["tier"]
    if tier == 1:
      cooldown = 3600
      mins_ = 60
    if tier == 2:
      cooldown = 2700
      mins_ = 45
    if tier == 3:
      cooldown = 1800
      mins_ = 30
    if int(time.time()) >= self.bot.db["economy"][str(itx.user.id)]["pets"]["last_hunt"] + cooldown or 1:
      self.bot.db["economy"][str(itx.user.id)]["balance"] += amt_of_coins
      self.bot.db["economy"][str(itx.user.id)]["pets"]["last_hunt"] = time.time()
      self.bot.db["economy"][str(itx.user.id)]["counting"]["hunt"] += 1
      msg, color = f"**{name}** went out hunting and brought back **{amt_of_coins}{coin}!** \nYou can upgrade your pet using `{self.bot.prefix}pet upgrade`.", green
      quest_msg = get_quest_rewards(itx, "hunt", True)
      if happiness <= 50:
        msg += "\n**Your pet is very unhappy and this will impact your pet's hunting motivation!** \nTip: Feed your pet and play with it to keep it happy!"

    elif time.time() < self.bot.db["economy"][str(itx.user.id)]["pets"]["last_hunt"] + cooldown:
      currenttime = int(time.time())
      last_hunt = self.bot.db["economy"][str(itx.user.id)]["pets"]["last_hunt"]
      mins_left = str(math.floor((mins_ - ((currenttime - last_hunt) % 3600) / 60)))
      secs_left = str(math.floor((60 - ((currenttime - last_hunt) % 3600) % 60)))
      msg = f"**{name}** just went out to hunt and needs to rest! **{name}** will be ready to hunt again in `{mins_left}m {secs_left}s`"
    msg += quest_msg
    embed = discord.Embed(title = "Hunting", description = msg, color = color)
    if random.randint(1, 2) == 1:
      embed.set_footer(text = f"Tip: Set your pet's name using {self.bot.prefix}pet name <name>")
    await itx.response.send_message(embed = embed)

async def setup(bot):
  await bot.add_cog(Pets(bot))