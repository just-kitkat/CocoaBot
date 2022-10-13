import discord, time, random, math, asyncio
from vars import *
from errors import *
from discord import app_commands
from typing import Literal, Optional
from datetime import timedelta, date, datetime
from discord.ext import commands

class ChestButtons(discord.ui.View):
  def __init__(self, itx, userID, diamonds, recall = False):
    self.userID = userID
    self.diamonds = diamonds
    self.value = False
    super().__init__(timeout=120)
    types = {"normal":5, "rare":25, "legendary":200}
    for type in types:
      self.add_item(OpenChest(userID, type, types, diamonds < types[type]))

  @discord.ui.button(label = "View Possible Loot", emoji = "🎁", style = discord.ButtonStyle.blurple, row = 4)
  async def view_loot(self, itx: discord.Interaction, button: discord.ui.Button):
    embed = discord.Embed(
      title = "Possibe Chest Loot",
      description = "Open a chest and stand a chance to get any of these loot!",
      color = blurple
    )
    # Chets Rewards
    for chest_type in chest_rewards:
      msg = ""
      for rarity in chest_rewards[chest_type]:
        msg += f"**{rarity.title()}:** \n"
        for item in chest_rewards[chest_type][rarity]:
          msg += f"- {item} \n"
      embed.add_field(name = f"{chest_type.title()} Chest", value = msg)
    await itx.response.send_message(embed = embed)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

class OpenChest(discord.ui.Button):
  def __init__(self, userID: int, chosen: str, types: dict, can_open: bool):
    self.userID = userID
    self.types = types
    self.chosen = chosen
    self.can_open = can_open
    super().__init__(style=discord.ButtonStyle.success, label=f"Open {chosen.title()} Chest")
    self.disabled = can_open

  async def callback(self, itx: discord.Interaction):
    view: ChestButtons = self.view
    itx.client.db["economy"][str(itx.user.id)]["diamonds"] -= self.types[self.chosen]
    view = ChestButtons(itx, itx.user.id, itx.client.db["economy"][str(itx.user.id)]["diamonds"])
    diamonds = itx.client.db["economy"][str(itx.user.id)]["diamonds"]
    embed = discord.Embed(
        title = "Chests",
        description = f"""
You currently have **{diamonds} {diamond}**

Normal Chest: **5 {diamond}**
Rare Chest: **25 {diamond}**
Legendary Chest: **200{diamond}**
""",
        color = blurple
      )
    await itx.response.edit_message(embed = embed, view = view)
    # Chest logic
    chance = random.randint(1, 101)
    if chance <= 60: luck = "common"
    if 60 < chance <= 99: luck = "rare"
    if chance == 100: luck = "legendary"
    reward = "5% Kitkat Multiplier" #random.choice(chest_rewards[self.chosen][luck])

    # Handle coins
    if reward.endswith("Coins"):
      if reward.startswith("Small"): amt = random.randint(1000, 20000)
      if reward.startswith("Medium"): amt = random.randint(10000, 50000)
      if reward.startswith("Large"): amt = random.randint(500000, 1000000)
      if reward.startswith("Cart"): amt = random.randint(1000000, 5000000)
      if reward.startswith("House"): amt = random.randint(2500000, 10000000)
      itx.client.db["economy"][str(itx.user.id)]["balance"] += amt
      msg = f"You have gained **{amt} {coin}**"

    # Handle Kitkat Multipler
    if reward.endswith("Kitkat Multiplier"):
      mult = int(reward.split("%")[0])
      itx.client.db["economy"][str(itx.user.id)]["kitkats_boost"] += mult
      msg = f"You have recieved a **{mult}%** Kitkat Multiplier!"

    # Handle Pet Food
    if reward.endswith("Pet Food"):
      amt = int(reward.split("x")[0])
      msg = f"You have gained **{amt} Pet Food** (WIP)"

    if reward.endswith("Upgrade"):
      if reward[5:].startswith("Worker"): amt = "workers"
      if reward[5:].startswith("Machine"): amt = "machine_level"
      itx.client.db["economy"][str(itx.user.id)][amt] += 1
      msg = f"Your **{amt.replace('_', ' ')}** has increased by 1"

    if reward.endswith(diamond):
      amt = int(reward.split(" ")[0])
      itx.client.db["economy"][str(itx.user.id)]["diamonds"] += amt
      msg = f"You have recieved **{amt} {diamond}**"

    if reward.endswith("Fish"):
      if reward.startswith("Small"): 
        fish = random.choice(["tuna", "grouper"])
        amt = random.randint(3, 8)
      if reward.startswith("Medium"): 
        fish = random.choice(["tuna", "grouper", "snapper"])
        amt = random.randint(5, 25)
      if reward.startswith("Large"): 
        fish = random.choice(["snapper", "salmon", "cod"])
        amt = random.randint(8, 30) if amt[0] != "cod" else random.randint(2, 5)
      itx.client.db["economy"][str(itx.user.id)]["fish"][fish] += amt
      msg = f"You received a bag of fish containing **{amt}x {fish}**"

    embed = discord.Embed(
      title = f"{self.chosen.title()} Chest",
      description = f"You spent **{self.types[self.chosen]} {diamond}** and opened a **{self.chosen.title()} Chest**! \nReward: **{reward}** \nRarity: **{luck.title()}** \n*{msg}*",
      color = blurple
    )
    
    await itx.followup.send(embed = embed)
    

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

  @discord.ui.button(label="Complete Quest", style = discord.ButtonStyle.blurple, row = 3)
  async def complete_quest(self, itx: discord.Interaction, button: discord.ui.Button):
    itx.client.db["economy"][str(itx.user.id)]["fish"][self.fish_name] -= itx.client.db["economy"][str(itx.user.id)]["quest"]["fish"]["times"]
    itx.client.db["economy"][str(itx.user.id)]["quest"]["fish"]["completed"] = True
    itx.client.db["economy"][str(itx.user.id)]["balance"] += 25000
    await itx.response.send_message("Quest completed!")
    

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)
    
  

class PrestigeButton(discord.ui.View):
  def __init__(self, userID, prestige, disabled):
    self.userID = userID
    self.prestige = prestige
    self.value = None
    super().__init__(timeout=180)
    self.prestige_button.disabled = disabled

  @discord.ui.button(label = "Prestige", style = discord.ButtonStyle.success)
  async def prestige_button(self, itx:discord.Interaction, button:discord.ui.Button):
    self.value = True
    button.disabled = True
    self.stop()
    await itx.response.edit_message(view=self)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID != itx.user.id:
      return await itx.client.itx_check(itx)
    return True

class Economy(commands.Cog, name = "General Commands"):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name = "start")
  async def start(self, itx: discord.Interaction):
    """Start your kitkat journey here!"""
    if str(itx.user.id) not in self.bot.db["economy"]:
      self.bot.db["economy"][str(itx.user.id)] = {"balance" : 10 , "last_sold" : int(time.time()), "workers" : 1, "machine_level" : 1, "storage" : 200, "last_daily" : 1, "last_weekly" : 1, "last_monthly" : 1, "prestige" : 0, "kitkats_sold" : 0, "last_cf": 1, "upgrade_cap" : 10, "sponsor" : 0, "diamonds" : 0, "kitkats_boost" : 0, "income": 100, "fish" : {"last_fish" : 0, "rod_level" : 1, "tuna" : 0, "grouper" : 0, "snapper" : 0, "salmon" : 0, "cod" : 0}, "pets" : {"name": "", "type": "", "tier" : 0, "level": 0, "last_hunt" : 1, "last_feed": 1, "last_play": 1, "food": 0}, "daily_streak" : 0, "games" : {"sliding_puzzle_8_moves": -1, "sliding_puzzle_8_time": -1}}
      embed = discord.Embed(
        title = "**Kitkat Factory**", 
        description = f"""
  Hello {itx.user.mention}, you have successfully built a factory! Welcome to your very own **Kitkat Factory!** 
  Currently, you are producing kitkats at a rate of `3 {choco} / minute`! To sell the kitkats, all you need to do is `{self.bot.prefix}sell`! 
  Making upgrades to your factory will increase your kitkats' value!
  Current kitkat value: **2 {coin} / kitkat**.
      
  To produce kitkats at a faster rate, you can either hire more workers or upgrade your machine! You can do `{self.bot.prefix}upgrades` for more information on that! To view your balance, you can do `{self.bot.prefix}balance`.
  You can also get your own pet by doing `{self.bot.prefix}pet`! Having a pet gives you access to the `{self.bot.prefix}hunt` command, which gives you a random amount of coins every hour!
  
  Lastly, `{self.bot.prefix}guide` will always be avaliable to those who are confused on how the factory works! You can also view the leaderboard using `{self.bot.prefix}leaderboard` and prestige using `{self.bot.prefix}prestige`. 
  
  To join giveaways, lotteries and more, you can join KitkatBot's official server by clicking [here](https://discord.gg/hhVwjFBJ2C)! Here's a free **10{coin}** to get you started on your journey. Remember to do `{self.bot.prefix}daily` everyday to claim a free gift, good luck!
  """, 
        color = discord.Color.green()
      )
      await itx.response.send_message(embed = embed)
    else:
      await itx.response.send_message(f"You already own a factory! Do `{self.bot.prefix}help economy` to see the commands you can use!")

  @factory_check()
  @app_commands.command(name = "tutorial")
  async def guide(self, itx: discord.Interaction):
    """A brief guide to KitkatBot!"""
    workers = self.bot.db["economy"][str(itx.user.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(itx.user.id)]["machine_level"]

    rate_of_kitkats = (workers + 2) * machine_lvl
    embed = discord.Embed(
      title = "**The kitkat factory guide!**", 
      description = f"""
Hello {itx.user.mention}, it looks like you are lost! Do not worry, `?guide` will always be avaliable to you! 

Currently, you are producing kitkats at a rate of `{rate_of_kitkats} {choco} / minute`! To sell the kitkats, all you need to do is `{self.bot.prefix}sell`! 
Making upgrades to your factory will increase your kitkats' value!
Current kitkat value: **2 {coin} / kitkat**.
      
To produce kitkats at a faster rate, you can either hire more workers or upgrade your machine! You can do `{self.bot.prefix}upgrades` for more information on that! To view your balance, you can do `{self.bot.prefix}balance`.
You can also get your own pet by doing `{self.bot.prefix}pet`! Having a pet gives you access to the `{self.bot.prefix}hunt` command, which gives you a random amount of coins every hour!

You can view the leaderboard using `{self.bot.prefix}leaderboard` and prestige using `{self.bot.prefix}prestige`. To join giveaways, lotteries and more, you can join KitkatBot's official server by clicking [here](https://discord.gg/hhVwjFBJ2C)! Remember to do `{self.bot.prefix}daily` everyday to claim a free gift, good luck!
""", 
      color = discord.Color.green()
    )
    await itx.response.send_message(embed = embed)

  @factory_check()
  @app_commands.command(name = "work")
  async def work(self, itx: discord.Interaction):
    """Work to sell chocolates to earn some money!"""
    # to self: add multipliers and boosters
    color = blurple
    last_sold = self.bot.db["economy"][str(itx.user.id)]["last_sold"]
    time_diff = int(time.time()) - last_sold
    if time_diff >= 60*10:
      workers = self.bot.db["economy"][str(itx.user.id)]["workers"]
      machine_level = self.bot.db["economy"][str(itx.user.id)]["machine_level"]
  
      const = workers * machine_level * 1000
      amt_sold = random.randint(const//2, const*2)
  
      self.bot.db["economy"][str(itx.user.id)]["balance"] += amt_sold
      self.bot.db["economy"][str(itx.user.id)]["last_sold"] = int(time.time())
      balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
      msg = f"You worked hard and earned **{amt_sold}{coin}** \nBalance: **{balance:,}{coin}**" # add chocolates sold -> therefore amt earned
    else:
      msg = "You cannot work so soon! \nCooldown: `10 mins`" # cooldown based on level/patreon
      color = red
    embed = discord.Embed(title = bot_name, description = msg, color = color)
    await itx.response.send_message(embed = embed)
  
  @app_commands.command(name = "fish")
  @factory_check()
  @is_owner()
  async def fish(self, itx: discord.Interaction):
    """Take a break and go fishing!"""
    view = "placeholder"
    fishes = fishdb = itx.client.db["economy"][str(itx.user.id)]["fish"]
    fishes = ["tuna", "grouper", "snapper", "salmon", "cod"]
    loop = True
    while loop:
      odds = random.randint(1, 101)
      level = self.bot.db["economy"][str(itx.user.id)]["fish"]["rod_level"]
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
      if time.time() < self.bot.db["economy"][str(itx.user.id)]["fish"]["last_fish"] + cooldown:
        view = None
        embed = discord.Embed(
          title = "Fishing", 
          description = f"You cannot fish so soon! You can fish once every **{cooldown} seconds**. \n*Upgrade your fishing rod to decrease the cooldown!*", 
          color = discord.Color.orange()
        )
        loop = False
        await itx.response.send_message(embed = embed)
      elif time.time() >= self.bot.db["economy"][str(itx.user.id)]["fish"]["last_fish"] + cooldown:
        luck = random.randint(1,100)
        if luck > 10:
          self.bot.db["economy"][str(itx.user.id)]["fish"][fish] += 1
          self.bot.db["economy"][str(itx.user.id)]["fish"]["last_fish"] = int(time.time())
          embed = discord.Embed(
            title = "Fishing", 
            description = f"You went fishing and caught a **{'LEGENDARY ' if fish == 'cod' else ''}{fish}**!", 
            color = discord.Color.green()
          )
        else:
          money = random.randint(100*level, 2500*level)
          self.bot.db["economy"][str(itx.user.id)]["balance"] -= money
          self.bot.db["economy"][str(itx.user.id)]["fish"]["last_fish"] = int(time.time())
          if self.bot.db["economy"][str(itx.user.id)]["balance"] < 0: self.bot.db["economy"][str(itx.user.id)]["balance"] = 0
          embed = discord.Embed(
            title = "Fishing", 
            description = f"You went fishing and fished out an eel! You got electrocuted and had to pay **{money}{coin}** to see the doctor", 
            color = discord.Color.red()
          )
        self.bot.cache["fishing_cooldown"]["users"][str(itx.user.id)] = int(time.time())
        view = FishButtons(itx.user.id, cooldown) if view is not None else None
        try:
          await itx.response.send_message(embed = embed, view = view)
        except:
          await itx.followup.send(embed = embed, view = view)
      if view is not None:
        await view.wait()
        if not view.value:
          loop = False
        
  # Upgrades Command
  @factory_check()
  @app_commands.command(name = "upgrade")
  async def upgrade(self, itx: discord.Interaction, name: Optional[Literal["workers", "machines", "storage", "capacity", "rod"]]):
    """Upgrades!!!"""
    workers = self.bot.db["economy"][str(itx.user.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(itx.user.id)]["machine_level"]
    storage = self.bot.db["economy"][str(itx.user.id)]["storage"]
    total_upgrades = workers + machine_lvl
    balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
    upgrade_cap = self.bot.db["economy"][str(itx.user.id)]["upgrade_cap"]
    title, color = "Upgrades", red
  
    upgrades_mult = 1.96
  
    rate_of_kitkats = (workers + 2) * machine_lvl
    machine_base_upgrade = 20
    workers_base_upgrade = 10
    storage_base_upgrade = 50
    cap_base_upgrade = 10
    machine_upgrade = math.floor(machine_base_upgrade * upgrades_mult ** machine_lvl)
    workers_upgrade = math.floor(workers_base_upgrade * upgrades_mult ** workers)
    cap_upgrade = math.floor((upgrade_cap - 5) ** 4)
    storage_upgrade = storage_base_upgrade * 2 + storage
    rod_level = self.bot.db["economy"][str(itx.user.id)]["fish"]["rod_level"]
    if rod_level < 5:
      rod_upgrade_ = 10000 * 4 ** rod_level
      rod_upgrade = f"{rod_upgrade_}{coin}"
    else: 
      rod_upgrade = "Max Level"
    if name is None:
      title = "Upgrades avaliable:"
      msg = f"""
Machine Upgrade: **{machine_upgrade}{coin}**
Machine Level: **{machine_lvl}**
Command: `{self.bot.prefix}upgrade machine`

Hire Workers: **{workers_upgrade}{coin}**
Number of workers: **{workers}**
Command: `{self.bot.prefix}upgrade workers`

Capacity Upgrade: **{cap_upgrade}{coin}**
Upgrades Capacity: **{upgrade_cap}**
Command: `{self.bot.prefix}upgrade capacity`

Storage Upgrade: **{storage_upgrade}{coin}**
Storage capacity: **{storage:,}**
Command: `{self.bot.prefix}upgrade storage`

Fishing Rod Upgrade: **{rod_upgrade}{coin}**
FIshing Rod level: **{rod_level}**
Command: `{self.bot.prefix}upgrade rod`

To upgrade your pet, you can use `{self.bot.prefix}pet upgrade`.

Current balance: **{balance:,}{coin}**  |  `{rate_of_kitkats:,}{choco} / minute`
Do `{self.bot.prefix}help economy` to see all economy commands!
"""
      color = discord.Color.blurple()
    elif name == "workers":
      if balance >= workers_upgrade:
        if upgrade_cap > total_upgrades:
          self.bot.db["economy"][str(itx.user.id)]["balance"] -= workers_upgrade
          self.bot.db["economy"][str(itx.user.id)]["workers"] += 1
          title = "Upgrade Successful!"
          msg, color = f"You spent {workers_upgrade:,}{coin} to hire another worker! \n`Total workers: {workers + 1}`", green
        else:
          msg = f"Your upgrade capacity is full! Do `{self.bot.prefix}upgrade capacity` to increase it."
      else: 
        msg = f"You do not have enough coins to hire another worker! You need **{(workers_upgrade - balance):,}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
  
    elif name == "storage":
      if balance >= storage_upgrade:
        self.bot.db["economy"][str(itx.user.id)]["balance"] -= storage_upgrade
        self.bot.db["economy"][str(itx.user.id)]["storage"] += storage * 2
        title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent {storage_upgrade:,}{coin} to upgrade your storage capacity! \n`Storage capacity: {storage * 2}`", green
      else: 
        msg = f"You do not have enough coins to upgrade your storage! You need **{(storage_upgrade - balance):,}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
  
    elif name == "machines":
      if balance >= machine_upgrade:
        if upgrade_cap > total_upgrades:
          self.bot.db["economy"][str(itx.user.id)]["balance"] -= machine_upgrade
          self.bot.db["economy"][str(itx.user.id)]["machine_level"] += 1
          title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent {machine_upgrade:,}{coin} to upgrade your machine! \nMachine level: `{machine_lvl + 1}`", green
        else:
          msg = f"Your upgrade capacity is full! Do `{self.bot.prefix}upgrade capacity` to increase it."
      else: 
        msg = f"You do not have enough coins to upgrade your machine! You need **{(machine_upgrade - balance):,}{coin} more!** Do `{self.bot.prefix}help economy` to explore other commands!"
    elif name == "capacity":
      if balance >= cap_upgrade:
        self.bot.db["economy"][str(itx.user.id)]["balance"] -= cap_upgrade
        self.bot.db["economy"][str(itx.user.id)]["upgrade_cap"] += 10
        title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent {cap_upgrade:,}{coin} to upgrade your upgrades capacity! \nCurrent Capacity: `{upgrade_cap + 10}`", green
      else: 
        msg = f"You do not have enough coins to upgrade your capacity! You need **{(cap_upgrade - balance):,}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
    elif name == "rod":
      if rod_level < 5:
        if balance >= rod_upgrade_:
          self.bot.db["economy"][str(itx.user.id)]["balance"] -= rod_upgrade_
          self.bot.db["economy"][str(itx.user.id)]["fish"]["rod_level"] += 1
          if rod_level + 1 == 3:
            extra = "\n**Congratulations, you have unlocked the ability to catch a *Salmon***!"
          elif rod_level + 1 == 5:
            extra = "\n**Congratulations, you have unlocked the ability to catch a *LEGENDARY Cod Fish***!"
          else:
            extra = "\n**Your fishing cooldown has decreased!**"
          title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent **{rod_upgrade_:,}{coin}** to upgrade your fishing rod! \nFishing rod level: `{rod_level + 1}` {extra}", green
        else: 
          msg = f"You do not have enough coins to upgrade your fishing rod! You need **{(rod_upgrade_ - balance):,}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
      else: 
        msg = "Your fishing rod is already maxed out!"
    embed = discord.Embed(title = title, description = msg, color = color)
    await itx.response.send_message(embed = embed)

  # Balance Command
  @app_commands.command(name = "balance")
  @factory_check()
  async def balance(self, itx: discord.Interaction, user: discord.Member = None):
    """View a user's balance or your own!"""
    if user is None:
      user = itx.user
    balance = self.bot.db["economy"][str(user.id)]["balance"]
    bal = f"{balance:,}"
    if user == itx.user:
      msg = f"Your balance is **{bal}{coin}**! \nYou can do `{self.bot.prefix}sell` to sell your current kitkats and earn more money!"
    else:
      msg = f"**{user.name}'s** balance is **{bal}{coin}!**"
    embed = discord.Embed(title = f"{user.name}'s balance", description = msg, color = green)
    await itx.response.send_message(embed = embed)

  # Stats Command 
  @factory_check()
  @app_commands.command(name = "statistics")
  async def stats(self, itx: discord.Interaction, user: discord.Member = None):
    """View someone's stats!"""
    if user is None:
      user = self.bot.get_user(itx.user.id)
    embed = discord.Embed(
      title = f"{user.name}'s profile:",
      description = f"Getting {user.name}'s statistics...", 
      color = discord.Color.blue()
    )
    embed.set_footer(text = f"Do {self.bot.prefix}profile <@user> to check someone's profile!")

    await itx.response.send_message(embed = embed)
    workers = self.bot.db["economy"][str(user.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(user.id)]["machine_level"]
    upgrade_cap = self.bot.db["economy"][str(user.id)]["upgrade_cap"]
    storage = self.bot.db["economy"][str(user.id)]["storage"]
    rate_of_kitkats = (workers + 2) * machine_lvl
    balance = self.bot.db["economy"][str(user.id)]["balance"]
    kitkats_sold = self.bot.db["economy"][str(user.id)]["kitkats_sold"]
    kitkats_boost = self.bot.db["economy"][str(user.id)]["kitkats_boost"]
    prestige = self.bot.db["economy"][str(user.id)]["prestige"]
    rod_level = self.bot.db["economy"][str(user.id)]["fish"]["rod_level"]
    daily_streak = self.bot.db["economy"][str(user.id)]["daily_streak"]
    msg = f"""
Balance: **{balance:,}{coin}** | `{rate_of_kitkats}{choco} / minute`

Machine Level: `{machine_lvl}`
Workers: `{workers}`
Upgrade Capacity: `{upgrade_cap}`
Kitkat Storage: `{storage}`
Fishing Rod Level: `{rod_level}`
Kitkats Multiplier: `{kitkats_boost}%`
Daily Streak: `{daily_streak}`
Total Kitkats Sold: `{kitkats_sold}{choco}`
"""
    
    if prestige > 0:
      msg += f"\nPrestige: `{prestige}`"
    else:
      msg += f"\nYou have not prestiged yet! Use `{self.bot.prefix}prestige` to prestige!"

    if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 0:
      msg += f"**\n\nPet Statistics: **{user.name} does not own a pet! \nDo `{self.bot.prefix}pet list` to view available pets!"

    elif self.bot.db["economy"][str(user.id)]["pets"]["tier"] > 0:
      pet_name = self.bot.db["economy"][str(user.id)]["pets"]["name"]
      pet_tier = self.bot.db["economy"][str(user.id)]["pets"]["tier"]
      pet_type = self.bot.db["economy"][str(user.id)]["pets"]["type"]
      pet_level = self.bot.db["economy"][str(user.id)]["pets"]["level"]
      last_hunt = int(self.bot.db["economy"][str(user.id)]["pets"]["last_hunt"])
      if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 1:
        cooldown = 3600
        mins_ = 60
      if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 2:
        cooldown = 2700
        mins_ = 45
      if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 3:
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
        last_hunt = self.bot.db["economy"][str(user.id)]["pets"]["last_hunt"]
        mins_left = str(math.floor((mins_ - ((currenttime - last_hunt) % 3600) / 60)))
        secs_left = str(math.floor((60 - ((currenttime - last_hunt) % 3600) % 60)))
        msg += f"\n`{pet_name}` can hunt again in `{mins_left}m {secs_left}s`"
      else: 
        msg += f"\n`{pet_name}` can go hunting! Do `{self.bot.prefix}hunt` to hunt!"
    new_embed = discord.Embed(
      title = f"{user.name}'s profile:",
      description = msg, color = discord.Color.green())
    new_embed.set_footer(text = f"Do {self.bot.prefix}profile <@user> to check someone's profile!")
    await itx.edit_original_response(embed = new_embed)

  @factory_check()
  @app_commands.command(name = "daily")
  async def daily(self, itx: discord.Interaction):
    """Collect your daily reward! """
    color = green
    workers = self.bot.db["economy"][str(itx.user.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(itx.user.id)]["machine_level"]
    balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
    last_daily = self.bot.db["economy"][str(itx.user.id)]["last_daily"]
    currenttime = int(time.time())
    rate_of_kitkats = (workers + 2) * machine_lvl
    daily_coins = int(rate_of_kitkats) * 100
    daily_streak = self.bot.db["economy"][str(itx.user.id)]["daily_streak"]
    
    if currenttime >= (last_daily + 86400):
      pres_coins = 0
      streak_bonus = 500
      if currenttime >= (last_daily + 86400*2):
        self.bot.db["economy"][str(itx.user.id)]["daily_streak"] = 0
        streak_coins = 0
      else:
        self.bot.db["economy"][str(itx.user.id)]["daily_streak"] += 1
      streak_coins = self.bot.db["economy"][str(itx.user.id)]["daily_streak"] * streak_bonus
        
      daily_streak = self.bot.db["economy"][str(itx.user.id)]["daily_streak"]
      if self.bot.db["economy"][str(itx.user.id)]["prestige"] >= 2:
        pres_coins = math.floor(daily_coins/100*15)
        rate = "15%"
        if self.bot.db["economy"][str(itx.user.id)]["prestige"] >= 3:
          pres_coins = math.floor(daily_coins/100*30)
          rate = "30%"
      total_coins = daily_coins + pres_coins + streak_coins

      self.bot.db["economy"][str(itx.user.id)]["last_daily"] = time.time()
      self.bot.db["economy"][str(itx.user.id)]["balance"] += total_coins
      updated_bal = balance + total_coins
      if self.bot.db["economy"][str(itx.user.id)]["prestige"] < 2:
        msg = f"Daily reward: **{daily_coins}{coin}** \nStreak Bonus: **{streak_coins}{coin}** \nTotal Reward: **{total_coins}{coin}** \n\nCurrent Balance: **{updated_bal}{coin}** \nDaily Streak: `{daily_streak}` "
      else: 
        msg = f"Daily reward: **{daily_coins}{coin}** \nPrestige bonus: **{pres_coins}{coin}** (+{rate}) \nStreak Bonus: **{streak_coins}{coin}** \nTotal Reward: **{total_coins}{coin}** \n\nCurrent Balance: **{updated_bal}{coin}** \nDaily Streak: `{daily_streak}` "
      
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
    await itx.response.send_message(embed = embed)

  @factory_check()
  @app_commands.command(name = "weekly")
  async def weekly(self, itx: discord.Interaction):
    """Collect your weekly reward!"""
    if self.bot.db["economy"][str(itx.user.id)]["prestige"] >= 1:
      workers = self.bot.db["economy"][str(itx.user.id)]["workers"]
      machine_lvl = self.bot.db["economy"][str(itx.user.id)]["machine_level"]
      balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
      last_weekly = self.bot.db["economy"][str(itx.user.id)]["last_weekly"]
      currenttime = int(time.time())
      rate_of_kitkats = (workers + 2) * machine_lvl
      weekly_coins = (int(rate_of_kitkats) + 20) * 800

      if currenttime >= (last_weekly + 604800):
        self.bot.db["economy"][str(itx.user.id)]["last_weekly"] = int(time.time())
        self.bot.db["economy"][str(itx.user.id)]["balance"] += weekly_coins
        msg, color = f"You have claimed your weekly gift of **{weekly_coins}{coin}!** \nCurrent balance: **{balance + weekly_coins}{coin}**", green
      else:
        td = timedelta(seconds=604800-currenttime+last_weekly)
        days_left = td.days
        hours_left = td.seconds // 3600
        mins_left = (td.seconds % 3600) // 60
        secs_left = td.seconds % 60
        msg, color = f"You can claim your weekly gift in `{days_left}d {hours_left}h {mins_left}m {secs_left}s`. ", red
    else:
      msg, color = f"This is a prestige 1 feature! Do `{self.bot.prefix}prestige` to view prestige costs!", red
    embed = discord.Embed(title = "Weekly Reward", description = msg, color = color)
    await itx.response.send_message(embed = embed)

  @factory_check()
  @app_commands.command(name = "monthly")
  async def monthly(self, itx: discord.Interaction):
    """Collect your monthly reward!"""
    workers = self.bot.db["economy"][str(itx.user.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(itx.user.id)]["machine_level"]
    balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
    last_monthly = self.bot.db["economy"][str(itx.user.id)]["last_monthly"]
    currenttime = int(time.time())
    rate_of_kitkats = (workers + 2) * machine_lvl
    monthly_coins = (int(rate_of_kitkats) + 20) * 2000

    if currenttime >= (last_monthly + 2592000):
      self.bot.db["economy"][str(itx.user.id)]["last_monthly"] = time.time()
      self.bot.db["economy"][str(itx.user.id)]["balance"] += monthly_coins
      msg, color = f"You have claimed your monthly gift of **{monthly_coins}{coin}!** \nCurrent balance: **{balance + monthly_coins}{coin}**", green
    else:
      td = timedelta(seconds=2592000-currenttime+last_monthly)
      days_left = td.days
      hours_left = td.seconds // 3600
      mins_left = (td.seconds % 3600) // 60
      secs_left = td.seconds % 60
      msg, color = f"You can claim your monthly gift in `{days_left}d {hours_left}h {mins_left}m {secs_left}s`. ", red
    embed = discord.Embed(title = "Monothly Reward", description = msg, color = color)
    await itx.response.send_message(embed = embed)

  @app_commands.command(name = "quests")
  @factory_check()
  @is_owner()
  async def quests(self, itx: discord.Interaction):
    """View your daily quests here!"""
    # 3 quests. 1 fishing, 1 hunting, 1 pet play/kitkats generated
    fish_msg, hunt_msg = await self.bot.check_quests(itx)
    last_quest = self.bot.db["economy"][str(itx.user.id)]["last_quest"]
    embed = discord.Embed(title = "Daily Quests", description = f"Quest resetting <t:{last_quest + 86400}:R>", color = blurple)
    embed.add_field(name = "Fishing Quest: ", value = fish_msg, inline = False)
    embed.add_field(name = "Hunting Quest: ", value = hunt_msg, inline = False)
    await itx.response.send_message(embed=embed)
        

  @factory_check()
  @app_commands.command(name = "prestige")
  async def prestige(self, itx: discord.Interaction):
    """View the hall of prestiges!"""
    prestige = self.bot.db["economy"][str(itx.user.id)]["prestige"]
    balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
    
    prestige_msg = f"""
Welcome to the hall of prestiges! Here, you can view all the prestige perks and can unlock the option to prestige!

Prestiges:
**[I]** - Unlocks a unique icon next to your name and bolds your name on the leaderboard. It also unlocks the `{self.bot.prefix}weekly` command which gives you A TON of coins EVERY WEEK!
Cost: **1,000,000{coin}**

**[II]** - Gives you an additional +15% coin bonus when recieving your daily gift.
Cost: **2,500,000{coin}**

**[III]** - Upgrades your daily bonus from +15% to +30%.
Cost: **5,000,000{coin}**

**[IV]** - You get an additional +5% coin bonus when selling kitkats.
Cost: **10,000,000{coin}**

**[V]** - Unlocks a special emoji next to your name on the leaderboards.
Cost: **20,000,000{coin}**

__More coming soon! :eyes:__


Current prestige: **[{prestige_icons[prestige]}]**
"""
    if prestige < 5:
      if balance >= eco_prestige[prestige + 1]:
        prestige_msg += f"\nYou have enough coins to prestige! Click the button to prestige! \n**WARNING:** This will reset ALL your progress!"
    elif prestige == 5:
      prestige_msg += f"\nYou are currently at the highest prestige level and cannot prestige anymore!"
    else:
      prestige_msg += f"You do not have enough coins to prestige! Coins needed: **{eco_prestige[prestige + 1]}{coin}**"

    embed = discord.Embed(
      title = "Prestige", 
      description = prestige_msg, 
        colour = discord.Color.blue()
        )
    view = PrestigeButton(itx.user.id, prestige, not (prestige < 5 and self.bot.db["economy"][str(itx.user.id)]["balance"] >= eco_prestige[prestige + 1]))
    prestige_confirm = await itx.response.send_message(embed = embed, view = view)
    await view.wait()
    if view.value:
      #self.bot.db["economy"][str(itx.user.id)] = {"balance" : 10 , "last_sold" : int(time.time()), "workers" : 1, "machine_level" : 1, "storage" : 200, "last_daily" : 1, "last_weekly" : 1, "last_monthly" : 1, "prestige" : 0, "kitkats_sold" : 0, "last_cf": 1, "upgrade_cap" : 10, "sponsor" : 0, "diamonds" : 0, "kitkats_boost" : 0, "fish" : {"last_fish" : 0, "rod_level" : 1, "tuna" : 0, "grouper" : 0, "snapper" : 0, "salmon" : 0, "cod" : 0}, "pets" : {"name": "", "type": "", "tier" : 0, "level": 0, "last_hunt" : 1, "last_feed": 1, "last_play": 1, "food": 0}, "daily_streak" : 0, "games" : {"sliding_puzzle_8_moves": -1, "sliding_puzzle_8_time": -1}}
      self.bot.db["economy"][str(itx.user.id)]["balance"] = 0
      self.bot.db["economy"][str(itx.user.id)]["last_sold"] = int(time.time())
      self.bot.db["economy"][str(itx.user.id)]["workers"] = 1
      self.bot.db["economy"][str(itx.user.id)]["machine_level"] = 1
      self.bot.db["economy"][str(itx.user.id)]["storage"] = 200
      self.bot.db["economy"][str(itx.user.id)]["upgrade_cap"] = 10
      self.bot.db["economy"][str(itx.user.id)]["last_daily"] = 1
      self.bot.db["economy"][str(itx.user.id)]["last_weekly"] = 1
      self.bot.db["economy"][str(itx.user.id)]["last_monthly"] = 1
      self.bot.db["economy"][str(itx.user.id)]["prestige"] += 1
      self.bot.db["economy"][str(itx.user.id)]["fish"] = {"last_fish" : 0, "rod_level" : 1, "tuna" : 0, "grouper" : 0, "snapper" : 0, "salmon" : 0, "cod" : 0}
      self.bot.db["economy"][str(itx.user.id)]["pets"] = {"name": "", "type": "", "tier" : 0, "level": 0, "last_hunt" : 1, "food": 0, "last_feed": 0, "last_play": 0}
      self.bot.db["economy"][str(itx.user.id)]["daily_streak"] = 0
        
      new_embed = discord.Embed(
          title=f"Prestige",
          description=f"You have successfully prestiged! **Prestige level: {prestige + 1}**",
          color=discord.Color.green())
      await itx.edit_original_response(embed = new_embed, view = None)
      p = self.bot.db["economy"][str(itx.user.id)]["prestige"]
      channel = self.bot.get_channel(971043716083089488)
      await channel.send(f"**{itx.user} has just prestiged! `Prestige {prestige} > {p}` [{itx.user.id}]**")
    elif view.value is None:
      embed = discord.Embed(title = "Prestige", description = prestige_msg + "\n*You did not click the button in time! Run the command again to prestige!*")
      await itx.edit_original_response(embed = embed)
    else:
      pass

  @factory_check()
  @app_commands.command(name = "leaderboard")
  async def leaderboard(self, itx: discord.Interaction, type: Optional[Literal["kitkats", "balance", "bugs", "sponsors"]]="kitkats"):
    """View the various leaderboards here!"""
    note = ""
    lb_dump = {}
    for user in self.bot.db["economy"]:
      if type in ("c", "coin", "coins", "bal", "balance"):
        lb_dump[user] = self.bot.db["economy"][user]["balance"]
        emoji = coin
        note = f"There are currently `{len(self.bot.db['economy'])}` users producing kitkats!"
        
      elif type in ("b", "bug", "bugs"):
        try:
          lb_dump[user] = self.bot.dbo["others"]["bugs"][user]
        except: 
          pass
        emoji = ":bug:"
        count = 0
        for user in self.bot.dbo['others']['bugs']:
          count += self.bot.dbo['others']['bugs'][user]
        note = f"A total of `{count}` bugs have been reported!"
        
      elif type in ("s", "sponsor", "sponsors"):
        lb_dump[user] = self.bot.db["economy"][user]["sponsor"]
        emoji = ":moneybag:"
        count = 0
        for user in self.bot.db["economy"]:
          count += self.bot.db["economy"][user]["sponsor"]
        note = f"A total of **{count:,} {coin}** has been sponsored!"
        
      else:
        lb_dump[user] = self.bot.db["economy"][user]["kitkats_sold"]
        emoji = choco
        note = f"There are currently `{len(self.bot.db['economy'])}` users producing kitkats!"
        
    lb = {users: balance for users, balance in reversed(sorted(lb_dump.items(), key=lambda item: item[1]))}
    
    count = 1
    msg = ""
    for user in lb:
      prestige = self.bot.db["economy"][user]["prestige"] if self.bot.db["economy"][user]["prestige"] <= 5 else 0
      fire = ":fire:" if prestige == 5 else ""
      custom_emoji = custom_emojis[user] if user in custom_emojis else ""
      tag = f"**{custom_emoji}{fire}[" + prestige_icons[prestige] + "]**"
        
      bal = lb[user]
      user = self.bot.get_user(int(user))
      msg += f"**{count}.** {tag} {user}: **{bal:,} {emoji}** \n"
      count += 1
      if count > 10: break
    msg += f"\n{note}"
    embed = discord.Embed(title = "Leaderboards", description = msg, color = green)
    await itx.response.send_message(embed = embed)

  @factory_check()
  @app_commands.command(name = "redeem")
  async def redeem(self, itx: discord.Interaction, code: str):
    """Redeem your KitkatBot code here!"""
    if code in self.bot.dbo["others"]["code"] and code is not None and str(itx.user.id) in self.bot.db["economy"]:
      money = self.bot.dbo["others"]["code"][code]
      self.bot.dbo["others"]["code"].pop(code)
      self.bot.db["economy"][str(itx.user.id)]["balance"] += money
      embed = discord.Embed(
        title = "Code claimed!",
        description = f"You have successfully claimed the code `{code}`. \nYou have earned **{money} {coin}**",
        color = discord.Color.blurple()
      )
      await itx.response.send_message(embed = embed)
      channel = bot.get_guild(923013388966166528).get_channel(968460468505153616)
      embed = discord.Embed(title = f"{itx.user} has claimed a code.", description = f"Code: `{code}` \nAmount: **{money} {coin}**", color = discord.Color.blurple())
      await channel.send(embed = embed)
    elif str(itx.user.id) not in self.bot.db["economy"]:
      raise FactoryCheck(f"Looks like you do not own a factory! Do `{self.bot.prefix}start` to build one!")
    else:
      embed = discord.Embed(
        title = "Code not found...",
        description = f"This code has been redeemed before or does not exist... Sorry.",
        color = discord.Color.red()
      )
      await itx.response.send_message(embed = embed)


  @app_commands.command(name = "chest")
  async def chest(self, itx: discord.Interaction):
    if str(itx.user.id) in self.bot.db["economy"]:
      diamonds = self.bot.db["economy"][str(itx.user.id)]["diamonds"]
      embed = discord.Embed(
        title = "Chests",
        description = f"""
You currently have **{diamonds} {diamond}**

Normal Chest: **5 {diamond}**
Rare Chest: **25 {diamond}**
Legendary Chest: **200{diamond}**
""",
        color = blurple
      )
      view = ChestButtons(itx, itx.user.id, diamonds)
      await itx.response.send_message(embed = embed, view = view)
      await view.wait()
      if view.value:
        pass
          
       

  @app_commands.command(name = "totalkitkats")
  async def totalkitkats(self, itx: discord.Interaction):
    """Total number of kitkats ever made!"""
    total = 0
    for user in self.bot.db["economy"]:
      total += self.bot.db["economy"][user]["kitkats_sold"]
    kitkats = f"{total:,}"
    await itx.response.send_message(f"A total of **{kitkats}{choco}** has been made!")
    
async def setup(bot):
  await bot.add_cog(Economy(bot))