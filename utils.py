import time
from datetime import timedelta
from typing import Optional, Literal
from errors import *
import discord
import asyncio
import random
import math
from vars import *

class FishingWelcomeButton(discord.ui.View):
  def __init__(self, userID):
    self.userID = userID
    self.value = False
    super().__init__(timeout=120)

  @discord.ui.button(label="Go Fishing", emoji="🎣", style=discord.ButtonStyle.success)
  async def start_fishing(self, itx: discord.Interaction, button: discord.ui.Button):
    self.value = True
    for child in self.children:
      child.disabled = True
    self.stop()
    await itx.response.edit_message(view=self)

  @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
  async def to_stats(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_stats(itx)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

class CraftRod(discord.ui.Button):
  def __init__(self, x: int, y: int):
    super().__init__(style=discord.ButtonStyle.success, label=f" ")
    self.x, self.y = x, y

  async def callback(self, itx: discord.Interaction):
    return
    view: FishButtons = self.view
    view.children[self.x*3 + self.y].label = ""
    await itx.response.edit_message(view = view)
    await view.sell_fish(view, itx, self.fish)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

class FishButtons(discord.ui.View):
  def __init__(self, userID, cooldown, *, timeout=5*60):
    self.userID = userID
    self.value = None
    self.cooldown = cooldown
    super().__init__(timeout=timeout)
    self.craft_rod.disabled = True
    
  @discord.ui.button(label="Fish Again", style = discord.ButtonStyle.green, emoji = "🎣")
  async def fish_again(self, itx:discord.Interaction, button:discord.ui.Button):
    if (str(self.userID) not in itx.client.cache["fishing_cooldown"]["users"] or itx.client.cache["fishing_cooldown"]["users"][str(itx.user.id)] + self.cooldown <= int(time.time())):
      itx.client.cache["fishing_cooldown"]["users"][str(itx.user.id)] = int(time.time()) 
      self.value = True
      for child in self.children:
        child.disabled = True
      self.stop()
      await itx.response.edit_message(view = self)
    else:
      time_left = itx.client.cache["fishing_cooldown"]["users"][str(itx.user.id)] + self.cooldown - int(time.time())
      embed = discord.Embed(title = "Fishing", description = f"{cross} You can only fish once every **{self.cooldown} seconds**! ({time_left}s left) \n*Upgrade your fishing rod to decrease the cooldown!*", color = red)
      await itx.response.send_message(embed = embed, ephemeral = True)

  @discord.ui.button(label = "View Inventory", style = discord.ButtonStyle.blurple, emoji = "🧰")
  async def view_inventory(self, itx: discord.Interaction, button: discord.ui.Button):
    await itx.client.check_quests(itx)
    fishdb = itx.client.db["economy"][str(itx.user.id)]["fish"]
    fishes = {
      "tuna": fishdb["tuna"],
      "grouper": fishdb["grouper"],
      "snapper": fishdb["snapper"],
      "salmon": fishdb["salmon"],
      "cod": fishdb["cod"]
    }
    msg = ""
    for fish in fishes:
      if fishes[fish] > 0:
        msg += f"**{fishes[fish]:,}x {fish.title()}** ({fish_values[fish]:,} {coin} each) \n"
    if msg == "":
      msg = f"You have not caught any fishes! Go do some fishing and come back!"

    embed = discord.Embed(title = "Fishing Inventory", description = msg, color = blurple)
    embed.set_footer(text = "Upgrade your rod to unlock different kinds of fishes!")
    view = SellFish(itx.user.id, itx.client)
    await itx.response.send_message(embed = embed, view = view)

  @discord.ui.button(label = "Craft New Rod", style = discord.ButtonStyle.blurple, emoji = "🧰")
  async def craft_rod(self, itx: discord.Interaction, button: discord.ui.Button):
    return

  @discord.ui.button(label = "Back", style = discord.ButtonStyle.blurple)
  async def to_stats(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_stats(itx)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

class SellIndiFish(discord.ui.Button):
  def __init__(self, fish):
    super().__init__(style=discord.ButtonStyle.success, label=f"Sell {fish.title()}")
    self.fish = fish

  async def callback(self, itx: discord.Interaction):
    view: SellFish = self.view
    self.disabled = True
    await itx.response.edit_message(view = view)
    await view.sell_fish(view, itx, self.fish)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)
    

class SellFish(discord.ui.View):
  def __init__(self, userID, dbval, *, timeout=5*60):
    self.userID = userID
    self.value = None
    self.dbval = dbval
    super().__init__(timeout=timeout)
    self.complete_quest.label = "Complete quest: Submit " + str(dbval.db["economy"][str(userID)]["quest"]["fish"]["times"]) + " " + dbval.db["economy"][str(userID)]["quest"]["fish"]["name"] + "s"
    self.fish_name = dbval.db["economy"][str(userID)]["quest"]["fish"]["name"]
    self.fish_needed = dbval.db["economy"][str(userID)]["quest"]["fish"]["times"]
    self.complete_quest.disabled = dbval.db["economy"][str(userID)]["quest"]["fish"]["completed"] or dbval.db["economy"][str(userID)]["fish"][self.fish_name] < self.fish_needed
    #self.sell_tuna.label = "tuna"
    fishdb = self.dbval.db["economy"][str(userID)]["fish"]
    fishes = {
    "tuna": fishdb["tuna"],
    "grouper": fishdb["grouper"],
    "snapper": fishdb["snapper"],
    "salmon": fishdb["salmon"],
    "cod": fishdb["cod"]
  }
    for fish in fishes:
      if fishes[fish] > 0:
        self.add_item(SellIndiFish(fish))

  async def sell_fish(self, ins, itx: discord.Interaction, type: str):
    await itx.edit_original_response(view = ins)
    fishdb = itx.client.db["economy"][str(itx.user.id)]["fish"]
    fishes = {
    "tuna": fishdb["tuna"],
    "grouper": fishdb["grouper"],
    "snapper": fishdb["snapper"],
    "salmon": fishdb["salmon"],
    "cod": fishdb["cod"]
  }
    temp = {type: fishes[type]} if type != True else fishes
    money = 0
    for fish in temp:
      money += fish_values[fish] * fishes[fish]
      itx.client.db["economy"][str(itx.user.id)]["fish"][fish] = 0

    itx.client.db["economy"][str(itx.user.id)]["balance"] += money
    balance = itx.client.db["economy"][str(itx.user.id)]["balance"]
    embed = discord.Embed(title = "Fish", description = f"You sold all your {'fishes' if type == True else type} for a total of **{money:,}{coin}**! \nBalance: **{balance:,}{coin}**", color = green)
    await itx.followup.send(embed = embed)
    
    
  @discord.ui.button(label="Sell All", style = discord.ButtonStyle.green, emoji = "💸")
  async def sell_all(self, itx: discord.Interaction, button: discord.ui.Button):
    for child in self.children:
      child.disabled = True
    await itx.response.edit_message(view = self)
    await self.sell_fish(self, itx, True)

  @discord.ui.button(label="Back", style = discord.ButtonStyle.green, row=4)
  async def to_stats(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_stats(itx)

  @discord.ui.button(label="Complete Quest", style = discord.ButtonStyle.blurple, row=3)
  async def complete_quest(self, itx: discord.Interaction, button: discord.ui.Button):
    itx.client.db["economy"][str(itx.user.id)]["fish"][self.fish_name] -= itx.client.db["economy"][str(itx.user.id)]["quest"]["fish"]["times"]
    itx.client.db["economy"][str(itx.user.id)]["quest"]["fish"]["completed"] = True
    itx.client.db["economy"][str(itx.user.id)]["balance"] += 25000
    await itx.response.send_message("Quest completed!")
    

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)
    

class BackButton(discord.ui.View):
  def __init__(self, user=None):
    self.user = user
    super().__init__(timeout=None)

  @discord.ui.button(label = "Back", style = discord.ButtonStyle.blurple)
  async def back_to_stats(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_stats(itx, self.user)

class StatsButtons(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(label = "Daily", style = discord.ButtonStyle.success)
  async def to_daily(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_daily(itx)

  @discord.ui.button(label = "Upgrades", style = discord.ButtonStyle.success)
  async def to_upgrade(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_upgrade(itx)

  @discord.ui.button(label = "Quests", style = discord.ButtonStyle.success)
  async def to_quests(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_quests(itx)

  @discord.ui.button(label = "Fish", style = discord.ButtonStyle.success)
  async def to_fish(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_fish(itx)

class UpgradesButton(discord.ui.View):
  def __init__(self, userID):
    self.userID = userID
    self.value = False
    super().__init__(timeout=None)

  @discord.ui.button(label = "Upgrade Again", style = discord.ButtonStyle.blurple)
  async def upgrade_again(self, itx: discord.Interaction, button: discord.ui.Button):
    self.value = True
    button.disabled = True
    await itx.response.edit_message(view=self)
    self.stop()

  @discord.ui.button(label = "Back", style = discord.ButtonStyle.blurple)
  async def back_to_stats(self, itx: discord.Interaction, button: discord.ui.Button):
    await get_stats(itx)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

async def get_daily(itx):
  color = green
  streak_msg = ""
  income = itx.client.db["economy"][str(itx.user.id)]["income"]
  balance = itx.client.db["economy"][str(itx.user.id)]["balance"]
  last_daily = itx.client.db["economy"][str(itx.user.id)]["last_daily"]
  currenttime = int(time.time())
  daily_coins = income * 5
  daily_streak = itx.client.db["economy"][str(itx.user.id)]["daily_streak"]
  
  if currenttime >= (last_daily + 86400):
    streak_bonus = 500
    if currenttime >= (last_daily + 86400*2):
      itx.client.db["economy"][str(itx.user.id)]["daily_streak"] = 1
      streak_msg = f"*You lost your **{daily_streak} days** daily streak!*"
    else:
      itx.client.db["economy"][str(itx.user.id)]["daily_streak"] += 1
    daily_streak = itx.client.db["economy"][str(itx.user.id)]["daily_streak"]
    streak_coins = itx.client.db["economy"][str(itx.user.id)]["daily_streak"] * streak_bonus if daily_streak != 1 else 0
      
    daily_streak = itx.client.db["economy"][str(itx.user.id)]["daily_streak"]
    total_coins = daily_coins + streak_coins
    xp_msg = await itx.client.check_xp(itx.user.id, 5)

    itx.client.db["economy"][str(itx.user.id)]["last_daily"] = time.time()
    itx.client.db["economy"][str(itx.user.id)]["balance"] += total_coins
    updated_bal = balance + total_coins
    msg = f"Daily reward: **{daily_coins}{coin}** \nStreak Bonus: **{streak_coins}{coin}** \nTotal Reward: **{total_coins}{coin}** \n\nCurrent Balance: **{updated_bal}{coin}** \nDaily Streak: `{daily_streak}` {xp_msg}\n{streak_msg}"
    
  else:
    td = timedelta(seconds=86400-currenttime+last_daily)
    hours_left = td.seconds // 3600
    mins_left = (td.seconds % 3600) // 60
    secs_left = td.seconds % 60
    msg, color = f"You can claim your daily gift in `{hours_left}h {mins_left}m {secs_left}s`. \nDaily Streak: `{daily_streak}`", red
    
  embed = discord.Embed(
      title = "Daily Reward",
      description = msg,
      color = color
    )
  view = BackButton()
  await itx.response.send_message(embed=embed, view=view)

async def get_stats(itx, user=None):
  if user is None:
    user = itx.client.get_user(itx.user.id)
    embed = discord.Embed(
      title = f"{user.name}'s profile:",
      description = f"Getting {user.name}'s statistics...", 
      color = discord.Color.blue()
    )
    embed.set_footer(text = f"Do {itx.client.prefix}profile <@user> to check someone's profile!")
    await itx.response.send_message(embed = embed)
    balance = itx.client.db["economy"][str(user.id)]["balance"]
    kitkats_sold = itx.client.db["economy"][str(user.id)]["kitkats_sold"]
    kitkats_boost = itx.client.db["economy"][str(user.id)]["kitkats_boost"]
    prestige = itx.client.db["economy"][str(user.id)]["prestige"]
    rod_level = itx.client.db["economy"][str(user.id)]["fish"]["rod_level"]
    daily_streak = itx.client.db["economy"][str(user.id)]["daily_streak"]
    income = itx.client.db["economy"][str(user.id)]["income"]
    msg = f"""
  Balance: **{balance:,}{coin} | {income} {coin} / hour**
  
  Fishing Rod Level: `{rod_level}`
  Kitkats Multiplier: `{kitkats_boost}%`
  Daily Streak: `{daily_streak}`
  Total Kitkats Sold: `{kitkats_sold}{choco}`
  """
    
    if prestige > 0:
      msg += f"\nPrestige: `{prestige}`"
    else:
      msg += f"\nYou have not prestiged yet! Use `{itx.client.prefix}prestige` to prestige!"
  
    if itx.client.db["economy"][str(user.id)]["pets"]["tier"] == 0:
      msg += f"**\n\nPet Statistics: **{user.name} does not own a pet! \nDo `{itx.client.prefix}pet list` to view available pets!"
  
    elif itx.client.db["economy"][str(user.id)]["pets"]["tier"] > 0:
      pet_name = itx.client.db["economy"][str(user.id)]["pets"]["name"]
      pet_tier = itx.client.db["economy"][str(user.id)]["pets"]["tier"]
      pet_type = itx.client.db["economy"][str(user.id)]["pets"]["type"]
      pet_level = itx.client.db["economy"][str(user.id)]["pets"]["level"]
      last_hunt = int(itx.client.db["economy"][str(user.id)]["pets"]["last_hunt"])
      if itx.client.db["economy"][str(user.id)]["pets"]["tier"] == 1:
        cooldown = 3600
        mins_ = 60
      if itx.client.db["economy"][str(user.id)]["pets"]["tier"] == 2:
        cooldown = 2700
        mins_ = 45
      if itx.client.db["economy"][str(user.id)]["pets"]["tier"] == 3:
        cooldown = 1800
        mins_ = 30
      msg += f"""\n\n**Pet Statistics:**
  Name: `{pet_name}`
  Type: `{pet_type}`
  Tier: `{pet_tier}`
  Level: `{pet_level}`
  """   
      if int(time.time()) < last_hunt + cooldown:
        currenttime = int(time.time())
        last_hunt = itx.client.db["economy"][str(user.id)]["pets"]["last_hunt"]
        mins_left = str(math.floor((mins_ - ((currenttime - last_hunt) % 3600) / 60)))
        secs_left = str(math.floor((60 - ((currenttime - last_hunt) % 3600) % 60)))
        msg += f"\n`{pet_name}` can hunt again in `{mins_left}m {secs_left}s`"
      else: 
        msg += f"\n`{pet_name}` can go hunting! Do `{itx.client.prefix}hunt` to hunt!"
    new_embed = discord.Embed(
      title = f"{user.name}'s profile:",
      description = msg, color = discord.Color.green())
    new_embed.set_footer(text = f"Do {itx.client.prefix}profile <@user> to check someone's profile!")
    view = StatsButtons()
    await itx.edit_original_response(embed=new_embed, view=view)

async def get_upgrade(itx: discord.Interaction, name: Optional[str]=None):
  """Upgrades!!!"""
  # TODO: Cocoa bean grinder, chocolate moudling machine, storage tank, chocolate freezer, packaging machine, workers
  # Formula for upgrades: base_cost * multiplier ** level (start from 1)
  title, color, multiplier = "Upgrades", blurple, 1.75
  upgrades_map = {
    "farm": ["farmer", "store", "van", "storage_tank", "warehouse"],
    "factory": ["bean_grinder", "chocolate_moulder", "chocolate_freezer", "workers", "chocolate_packager"]
  }
  # [a for a in [i for i in list(upgrades_map.values())]]
  for upgrade_location in upgrades_map:
    if name in upgrades_map[upgrade_location]:
      upgrade_type = upgrade_location
      break
  if name is not None and upgrade_type not in itx.client.db["economy"][str(itx.user.id)]["unlocked_upgrades"]: 
    embed = discord.Embed(title=title, description=f"{cross} You have not unlocked the **{upgrade_type}** yet! \nSee `{itx.client.prefix}upgrade` for available upgrades.")
    await itx.response.send_message(embed=embed, ephemeral=True)
    return

  base_upgrades = {
    "farmer": 50, "store": 250, "van": 5000, "storage_tank": 800, "warehouse": 500,
    "bean_grinder": 2500, "chocolate_moulder": 6500, "chocolate_freezer": 9000, "workers": 25000, "chocolate_packager": 12000
  }
  upgrade_again = True
  while upgrade_again:
    upgrade_again = False
    upgrades = {}
    upgrades.update(itx.client.db["economy"][str(itx.user.id)]["upgrades"]["farm"])
    upgrades.update(itx.client.db["economy"][str(itx.user.id)]["upgrades"]["factory"])
    #Farm
    upgrades["farmer"]["income"] = 20
    upgrades["farmer"]["coords"] = (250, 200)
    upgrades["store"]["income"] = 50
    upgrades["store"]["coords"] = (800, 200)
    upgrades["van"]["income"] = 120
    upgrades["van"]["coords"] = (860, 300)
    upgrades["storage_tank"]["income"] = 100
    upgrades["storage_tank"]["coords"] = (1000, 500)
    upgrades["warehouse"]["income"] = 90
    upgrades["warehouse"]["coords"] = (400, 500)
    # Factory 
    upgrades["bean_grinder"]["income"] = 100
    upgrades["bean_grinder"]["coords"] = (250, 200)
    upgrades["chocolate_moulder"]["income"] = 250
    upgrades["chocolate_moulder"]["coords"] = (800, 200)
    upgrades["chocolate_freezer"]["income"] = 420
    upgrades["chocolate_freezer"]["coords"] = (800, 350)
    upgrades["workers"]["income"] = 600 #workers more = less mechenical breakdown
    upgrades["workers"]["coords"] = (800, 450)
    upgrades["chocolate_packager"]["income"] = 550
    upgrades["chocolate_packager"]["coords"] = (250, 450)

    # cost 
    for upgrade in upgrades:
      upgrades[upgrade]["cost"] = int(base_upgrades[upgrade]*multiplier**(upgrades[upgrade]["level"] - 1))

    if name is None:
      msg = ""
      for upgrade in upgrades_map["farm"]:
        msg += f"{upgrades[upgrade]['name']} | `{upgrades[upgrade]['level']}/{upgrades[upgrade]['max']}` \nIncome: **{upgrades[upgrade]['income']} {coin} / hr** \nCost: **{upgrades[upgrade]['cost']} {coin}** \n\n"
      embed = discord.Embed(title = title, description = msg, color = color)
      #embed.set_image(url="attachment://temp.png")
      view = BackButton()
      await itx.response.send_message(embed = embed, view=view) #file=file when img added
    else:
      cost = upgrades[name]["cost"]
      balance = itx.client.db["economy"][str(itx.user.id)]["balance"]
      if balance >= cost and upgrades[name]["level"] < upgrades[name]["max"]:
        itx.client.db["economy"][str(itx.user.id)]["upgrades"][upgrade_type][name]["level"] += 1
        itx.client.db["economy"][str(itx.user.id)]["balance"] -= cost
        itx.client.db["economy"][str(itx.user.id)]["income"] += upgrades[name]["income"]
        balance -= cost
        income = itx.client.db["economy"][str(itx.user.id)]["income"]
        level = itx.client.db["economy"][str(itx.user.id)]["upgrades"][upgrade_type][name]["level"]
        xp_msg = await itx.client.check_xp(itx.user.id, math.floor(level**(4/5)))
        msg, color, ephemeral = f"You have upgraded your **{name}** to **level {level}** \nBalance: **{balance} {coin}** \nIncome: **{income} {coin} / hr** {xp_msg}", green, False # make a upgrade again button
        view = UpgradesButton(itx.user.id)
      elif upgrades[name]["level"] >= upgrades[name]["max"]:
        msg, color, ephemeral = f"You have maxed out this upgrade!", red, True
      else:
        msg, color, ephemeral = f"You do not have enough money for this upgrade! \nBalance: **{balance} {coin}** \nAmount needed: **{cost} {coin}**", red, True
      embed = discord.Embed(title = "Upgrade", description = msg, color = color)
      try: #itx.response.is_done
        await itx.response.send_message(embed=embed, ephemeral=ephemeral, view=view)
      except Exception:
        await itx.followup.send(embed=embed, ephemeral=ephemeral, view=view)
      if view is None: break
      await view.wait()
      if view.value:
        upgrade_again = True

@is_owner()
async def get_quests(itx):
# 3 quests. 1 fishing, 1 hunting, 1 pet play/kitkats generated
  fish_msg, hunt_msg = await itx.client.check_quests(itx)
  last_quest = itx.client.db["economy"][str(itx.user.id)]["last_quest"]
  embed = discord.Embed(title = "Daily Quests", description = f"Quest resetting <t:{last_quest + 86400}:R>", color = blurple)
  embed.add_field(name = "Fishing Quest: ", value = fish_msg, inline = False)
  embed.add_field(name = "Hunting Quest: ", value = hunt_msg, inline = False)
  view = BackButton()
  await itx.response.send_message(embed=embed, view=view)

async def get_fish(itx: discord.Interaction):
  view = "placeholder"
  fishdb = itx.client.db["economy"][str(itx.user.id)]["fish"]
  fishes = ["tuna", "grouper", "snapper", "salmon", "cod"]
  
  loop, first_loop = True, True
  while loop:
    odds = random.randint(1, 101)
    level = itx.client.db["economy"][str(itx.user.id)]["fish"]["rod_level"]
    if level == 1:
      cooldown = 15
      if odds < 65: fish = "tuna"
      if 65 <= odds < 90: fish = "grouper"
      if odds >= 90: fish = "snapper"
    if level == 2:
      cooldown = 10
      if odds < 60: fish = "tuna"
      if 60 <= odds < 85: fish = "grouper"
      if odds >= 85: fish = "snapper"
    if level == 3:
      cooldown = 10
      if odds < 50: fish = "tuna"
      if 50 <= odds < 75: fish = "grouper"
      if 75 <= odds < 90: fish = "snapper"
      if odds >= 90: fish = "salmon"
    if level == 4:
      cooldown = 5
      if odds < 40: fish = "tuna"
      if 40 <= odds < 65: fish = "grouper"
      if 65 <= odds < 85: fish = "snapper"
      if odds >= 85: fish = "salmon"
    if level == 5:
      cooldown = 5
      if odds < 30: fish = "tuna"
      if 30 <= odds < 60: fish = "grouper"
      if 60 <= odds < 90: fish = "snapper"
      if 90 <= odds < 100: fish = "salmon"
      if odds >= 100: fish = "cod"
    cooldown = 1 # temp for testing
    if first_loop:
      embed = discord.Embed(
        title="Fishing Stats",
        description=f"""
  Total Fish Caught: TODO
  Rod Level: **{level}**
  Fishing Cooldown: **{cooldown}s**
  \nTip: *Upgrade your rod to decrease cooldowns and increase rewards!*
  """,
        color=blurple
      )
      view = FishingWelcomeButton(itx.user.id)
      await itx.response.send_message(embed=embed, view=view)
      first_loop = False
      await view.wait()
      if not view.value:
        return
    if time.time() < itx.client.db["economy"][str(itx.user.id)]["fish"]["last_fish"] + cooldown:
      view = None
      embed = discord.Embed(
        title = "Fishing", 
        description = f"You cannot fish so soon! You can fish once every **{cooldown} seconds**. \n*Upgrade your fishing rod to decrease the cooldown!*", 
        color = discord.Color.orange()
      )
      loop = False
      view = BackButton()
      await itx.response.send_message(embed=embed, view=view)
    elif time.time() >= itx.client.db["economy"][str(itx.user.id)]["fish"]["last_fish"] + cooldown:
      luck = random.randint(1,100)
      if luck > 10:
        itx.client.db["economy"][str(itx.user.id)]["fish"][fish] += 1
        itx.client.db["economy"][str(itx.user.id)]["fish"]["last_fish"] = int(time.time())
        embed = discord.Embed(
          title = "Fishing", 
          description = f"You went fishing and caught a **{'LEGENDARY ' if fish == 'cod' else ''}{fish}**!", 
          color = discord.Color.green()
        )
      else:
        money = random.randint(100*level, 2500*level)
        itx.client.db["economy"][str(itx.user.id)]["balance"] -= money
        itx.client.db["economy"][str(itx.user.id)]["fish"]["last_fish"] = int(time.time())
        if itx.client.db["economy"][str(itx.user.id)]["balance"] < 0: itx.client.db["economy"][str(itx.user.id)]["balance"] = 0
        embed = discord.Embed(
          title = "Fishing", 
          description = f"You went fishing and fished out an eel! You got electrocuted and had to pay **{money}{coin}** to see the doctor", 
          color = discord.Color.red()
        )
      itx.client.cache["fishing_cooldown"]["users"][str(itx.user.id)] = int(time.time())
      view = FishButtons(itx.user.id, cooldown) if view is not None else None
      try:
        await itx.response.send_message(embed = embed, view = view)
      except:
        await itx.followup.send(embed = embed, view = view)
    if view is not None:
      await view.wait()
      if not view.value:
        loop = False