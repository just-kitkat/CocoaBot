import discord
import time
import random
import math
import asyncio
from vars import *
from utils import *
from errors import *
from discord import app_commands
from typing import Literal, Optional
from datetime import timedelta
from discord.ext import commands
from discord.ext.commands import GroupCog
from discord.app_commands import Choice, Group, command
from PIL import ImageFont, ImageDraw, Image
from pilmoji import Pilmoji

async def buy_item(itx, item: str):
  """
  Handles shop purchases!
  """
  if item.endswith(diamond) or item.endswith(coin):
    amt = int(item.split(" ")[0])
    itx.client.db["economy"][str(itx.user.id)]["balance" if item.endswith(coin) else "diamonds"] += amt
  else:
    dur_def = {"h": 1, "d": 24, "w": 24*7}
    info = item.split(" ")
    mult = info[0][:-1]
    duration = int(info[-1][1:-2])*int(dur_def[info[-1][-2]])
    type_ = info[2]
    mag = info[1]

    if mag == "personal":
      itx.client.db["economy"][str(itx.user.id)]["boosts"][type_.lower()].append(
        {mult: duration}
      )
    elif mag == "global":
      itx.client.dbo["others"]["global_income_boost"] = {mult: duration}

class LocationButtons(discord.ui.View):
  def __init__(self, userID, next_location=None, disabled=True):
    self.userID = userID
    self.value = False
    super().__init__(timeout=120)
    if next_location is not None:
      self.unlock_location.label = f"Unlock {next_location.title()}"
    if next_location is None or not disabled:
      self.unlock_location.disabled = True
    self.add_item(CallBackButton())

  @discord.ui.button(label = "You have unlocked all locations", emoji = "🎁", style = discord.ButtonStyle.blurple)
  async def unlock_location(self, itx: discord.Interaction, button: discord.ui.Button):
    self.value = True
    self.stop()
    button.disabled = True
    await itx.response.edit_message(view=self)

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)
    
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
    reward = random.choice(chest_rewards[self.chosen][luck])

    # Handle coins
    if reward.endswith("Coins"):
      amt = -1 # will display this if it didnt get a reward (error)
      if reward.startswith("Small"): amt = random.randint(1000, 20000)
      if reward.startswith("Medium"): amt = random.randint(10000, 50000)
      if reward.startswith("Large"): amt = random.randint(500000, 1000000)
      if reward.startswith("Cart"): amt = random.randint(1000000, 5000000)
      if reward.startswith("House"): amt = random.randint(2500000, 10000000)
      itx.client.db["economy"][str(itx.user.id)]["balance"] += amt
      msg = f"You have gained **{amt} {coin}**"

    # Handle Income Multipler
    if reward.endswith("Income Multiplier"):
      mult = int(reward.split("%")[0])
      itx.client.db["economy"][str(itx.user.id)]["income_boost"] += mult
      msg = f"You have recieved a **{mult}%** Income Multiplier!"

    # Handle Pet Food
    if reward.endswith("Pet Food"):
      amt = int(reward.split("x")[0])
      msg = f"You have gained **{amt} Pet Food** (WIP)"

    if reward.endswith("Upgrade"):
      """
      if reward[5:].startswith("Worker"): amt = "workers"
      if reward[5:].startswith("Machine"): amt = "machine_level"
      itx.client.db["economy"][str(itx.user.id)][amt] += 1
      msg = f"Your **{amt.replace('_', ' ')}** has increased by 1"
      """
      msg = "This reward has been disabled, please create a support ticket to recieve compensation. reward: " + reward

    if reward.endswith(diamond):
      amt = int(reward.split(" ")[0])
      itx.client.db["economy"][str(itx.user.id)]["diamonds"] += amt
      msg = f"You have recieved **{amt} {diamond}**"

    if reward.endswith(ticket):
      amt = int(reward.split(" ")[0])
      itx.client.db["economy"][str(itx.user.id)]["golden_ticket"] += amt
      msg = f"You have recieved **{amt} {ticket}**"

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
  
class Economy(commands.Cog, name = "General Commands"):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name = "start")
  async def start(self, itx: discord.Interaction):
    """Start your chocolate journey here!"""
    if str(itx.user.id) not in self.bot.db["economy"]:
      self.bot.db["economy"][str(itx.user.id)] = {
        "balance": 100 , "last_sold": int(time.time()), "last_quest": 1, "last_clean": 1,
        "last_daily": 1, "last_weekly": 1, "last_monthly": 1, "daily_streak": 0, 
        "last_cf": 1, "cleanliness": 100,
        "golden_ticket": 0, "claimed_ticket": False, "account_age": int(time.time()),
        "bought_from_shop": [],
        "sponsor": 0, "diamonds": 0, "income_boost": 0, "income": 100, "bugs_found": 0,
        "unlocked_upgrades": ["farm"],
        "counting": {"work": 0, "hunt": 0, "fish": 0},
        "levels": {"xp" : 0, "xp_mult" : 1, "level" : 1, "xp_needed" : 20}, 
        "boosts": {"income": [], "xp": []}, # "income": [{mult: duration (s)}]
        "upgrades": {
          "farm": {
            "farmer": {"name": f"Farmer", "max": 10, "level": 1},
            "store": {"name": f"Store", "max": 8, "level": 1}, 
            "van": {"name": f"Delivery Van", "max": 6, "level": 0},
            "storage_tank": {"name": f"Storage Tank", "max": 8, "level": 1},
            "warehouse": {"name": f"Warehouse", "max": 12, "level": 1},
           },
          "factory": {
            "bean_grinder": {"name": f"Bean Grinder", "max": 10, "level": 1},
            "chocolate_moulder": {"name": f"Chocolate Moulder", "max": 8, "level": 1},
            "chocolate_freezer": {"name": f"Chocolate Freezer", "max": 5, "level": 1},
            "workers": {"name": f"Worker", "max": 12, "level": 1},
            "chocolate_packager": {"name": f"Chocolate Packager", "max": 5, "level": 1},
          },
          "distribution_center": {
            "fork_lifts": {"name": f"Fork Lifts", "max": 15, "level": 1},
            "packaging_machine": {"name": f"Packaging Machine", "max": 15, "level": 1},
            "storage_shelves": {"name": f"Storage Shelves", "max": 12, "level": 1},
            "trucks": {"name": f"Trucks", "max": 8, "level": 1},
            "managers": {"name": f"Managers", "max": 10, "level": 1},
          }
        }, 
        "fish": {
          "last_fish": 0, "rod_level": 1, "tuna": 0, "grouper": 0, "snapper": 0, "salmon": 0, "cod": 0
        }, 
        "pets": {
          "name": "", "type": "", "tier": 0, "level": 0, "last_hunt": 1, "last_feed": 1, "last_play": 1, "food": 0, 
        },
        "quest": {
          "fish": {"name": "tuna", "times": 5, "completed": False},
          "hunt": {"times": 1, "times_completed": 0, "completed": False},
          "income": {"times": 1, "times_completed": 0, "completed": False}
        },
        "games": {
          "sliding_puzzle_8_moves": -1, "sliding_puzzle_8_time": -1
        }
      }
      embed = discord.Embed(
        title = "Your brand new farm is now in business!", 
        description = f"Use `{self.bot.prefix}tutorial` to get started!", 
        color = discord.Color.green()
      )
      await itx.response.send_message(embed = embed)
    else:
      await itx.response.send_message(f"You already own a farm! Do `{self.bot.prefix}tutorial` to get started!", ephemeral=True)

  @factory_check()
  @app_commands.command()
  async def tutorial(self, itx: discord.Interaction):
    """A brief guide to CocoaBot!"""

    income = self.bot.db["economy"][str(itx.user.id)]["income"]
    embed = discord.Embed(
      title = "**Your chocolate farm guide!**", 
      description = f"""
Hello {itx.user.mention}, it looks like you are lost! Do not worry, `{self.bot.prefix}tutorial` will always be avaliable to you! 

➼ You are earning hourly income at a rate of **{income} {coin} / hour**! 
➼ You can **work** for extra income! (`{self.bot.prefix}work`)
➼ Upgrade your farm using `{self.bot.prefix}upgrade`, which will increase your hourly income.
➼ Unlock new locations with `{self.bot.prefix}location`
➼ Make sure to `{self.bot.prefix}clean` your shop often to keep your customers happy!
➼ Work on daily quests to earn amazing prizes.
➼ Collect your **daily**, **weekly** and **monthly** rewards!
➼ Adopt your very own pet with `{self.bot.prefix}pets list`. Having a pet gives you access to the `{self.bot.prefix}hunt` command and many other perks!
➼ Be the most successful farm and climb up the leaderboards! (`{self.bot.prefix}leaderboard`). 

➼ [Click Here]({disc_invite}) to join our discord server! 
Benefits:
➼ Frequent lotteries and giveaways
➼ Make new friends
➼ Keep up to date with new updates
➼ And many more...
""", 
      color = discord.Color.green()
    )
    await itx.response.send_message(embed = embed, ephemeral=True)

  @factory_check()
  @app_commands.command(name = "work")
  async def work(self, itx: discord.Interaction):
    """Work and earn some extra income!"""
    await get_work(itx)
  
  @app_commands.command(name = "fish")
  @factory_check()
  async def fish(self, itx: discord.Interaction):
    """Take a break and go fishing!"""
    await get_fish(itx)
    
  # Upgrades Command
  upgrades_group = Group(name="upgrades", description="Upgrades!! :D")
  
  @factory_check()
  @upgrades_group.command(name="buy")
  @app_commands.choices(
    name = [
      Choice(name="Farmer", value="farmer"),
      Choice(name="Store", value="store"),
      Choice(name="Delivery Van", value="van"),
      Choice(name="Storage Tank", value="storage_tank"),
      Choice(name="Warehouse", value="warehouse"),
      Choice(name="Bean Grinder", value="bean_grinder"),
      Choice(name="Chocolate Moulder", value="chocolate_moulder"),
      Choice(name="Chocolate Freezer", value="chocolate_freezer"),
      Choice(name="Worker", value="workers"),
      Choice(name="Chocolate Packager", value="chocolate_packager"),
      Choice(name="Fork Lifts", value="fork_lifts"),
      Choice(name="Packaging Machine", value="packaging_machine"),
      Choice(name="Storage Shelves", value="storage_shelves"),
      Choice(name="Trucks", value="trucks"),
      Choice(name="Managers", value="managers")
    ]
  )
  async def buy_upgrades(self, itx: discord.Interaction, name: str):
    """Upgrades!!!"""
    await get_upgrade(itx, "buy", name)

  @factory_check()
  @upgrades_group.command(name="view")
  async def view_upgrades(self, itx: discord.Interaction, location: Optional[Literal["Farm", "Factory", "Distribution Center"]]="Farm"):
    """View all upgrades!"""
    await get_upgrade(itx, "view", location)


  @factory_check()
  @app_commands.command(name="clean")
  async def clean(self, itx: discord.Interaction):
    """Clean your farm!"""
    last_clean = self.bot.db["economy"][str(itx.user.id)]["last_clean"]
    if last_clean + 3600*6 <= int(time.time()):
      self.bot.db["economy"][str(itx.user.id)]["cleanliness"] = 100
      self.bot.db["economy"][str(itx.user.id)]["last_clean"] = int(time.time())
      embed = discord.Embed(title="What a clean place!", description="You have cleaned your farm! \nCleanliness: **100%**", color=green)
    else:
      embed = discord.Embed(title = "Too clean!", description = "You cannot clean your farm so often! \nCooldown: `6 hours`", color=red)
    await itx.response.send_message(embed=embed)

  @factory_check()
  @app_commands.command(name="location")
  async def location(self, itx: discord.Interaction):
    """Unlock different locations for more upgrades!"""
    locations = {
      "farm": {"perks": [None], "requirements": [None]}, 
      "factory": {
        "perks": [
          "0.5x income boost", "0.25x XP boost", "More upgrades", f"20 {diamond}"
          ], 
        "requirements": [
          f"500,000 {coin}", f"3 {ticket}", "Level 25"
          ]}, 
      "distribution center": {
        "perks": [
          "0.75x income boost", "0.5x XP boost", "More upgrades", f"50 {diamond}"
          ],
        "requirements": [
          f"2,500,000 {coin}", f"8 {ticket}", "Level 50"
          ]}
    }
    unlocked = self.bot.db["economy"][str(itx.user.id)]["unlocked_upgrades"]
    next_location = None if unlocked[-1] == "distribution center" else list(locations)[list(locations).index(unlocked[-1]) + 1]

    def check_req(location: str, req: str=None):
      if location is None: return False
      reqs = locations[location]["requirements"] if req is None else [req]
      userstats = itx.client.db["economy"][str(itx.user.id)]
      meet_req = True
      for req in reqs:
        if req.endswith(coin) and userstats["balance"] < int(req[:-len(coin)].replace(",", "")): meet_req = False
        if req.endswith(ticket) and userstats["golden_ticket"] < int(req[:-len(ticket)]): meet_req = False
        if req.startswith("Level") and userstats["levels"]["level"] < int(req[6:]): meet_req = False

      return meet_req
    
    msg = ""
    if next_location is not None:
      msg += f"\nNext location: **{next_location.title()}** \n**Perks:** \n"
      for perk in locations[next_location]["perks"]:
        msg += f"- **{perk}**\n"
      msg += "\n**Requirements:** \n"
      for req in locations[next_location]["requirements"]:
        emoji = tick if check_req(next_location, req) else cross
        msg += f"{emoji} **{req}**\n"
    else: 
      msg += "**You have unlocked all locations!**"
    msg += "\nLocations unlocked: \n"
    for loc in unlocked:
      msg += f"- **{loc.title()}** \n"

    embed = discord.Embed(title="Locations", description=msg, color=blurple)
    view = LocationButtons(itx.user.id, next_location, check_req(next_location))
    await itx.response.send_message(embed=embed, view=view)
    await view.wait()
    if view.value:
      self.bot.db["economy"][str(itx.user.id)]["unlocked_upgrades"].append(next_location.replace(" ", "_"))
      for reward in locations[next_location]["perks"]:
        if reward.endswith("income boost"): self.bot.db["economy"][str(itx.user.id)]["income_boost"] += float(reward.split("x")[0])
        if reward.endswith("XP boost"): self.bot.db["economy"][str(itx.user.id)]["levels"]["xp_mult"] += float(reward.split("x")[0])
        if reward.endswith(diamond): self.bot.db["economy"][str(itx.user.id)]["diamonds"] += int(reward.split(diamond)[0][:-1]) # [:-1] is to remove the space, i.e. "50 " -> "50"
      msg = f"You have unlocked the **{next_location}** and recieved your rewards! \nUse `{prefix}upgrades view` to see your new upgrades!"
      embed = discord.Embed(title="New Location Unlocked", description=msg, color=green)
      await itx.followup.send(embed=embed)


  # Shop
  @app_commands.command(name = "shop")
  @factory_check()
  async def shop(self, itx: discord.Interaction):
    """
    Check out your shop offers!
    """
    items = self.bot.dbo["others"]["shop_items"]
    bought = self.bot.db["economy"][str(itx.user.id)]["bought_from_shop"]
    msg = "Welcome to the shop! \nWe offer new items everyday so come back tomorrow for even more deals! \n"

    for item in items:
      msg += f"""
{':lock: ' if item in bought else ''}**{item}**
Cost: **{items[item]} {ticket}**

"""
    msg += f"Buy items using `{prefix}buy <item>` \nShop reset <t:{self.bot.dbo['others']['last_shop_reset'] + 3600*24}:R>"
    embed = discord.Embed(
      title = "Shop",
      description = msg,
      color = blurple
    )
    await itx.response.send_message(embed=embed)

  # Buy
  @app_commands.command(name = "buy")
  @factory_check()
  async def buy(self, itx: discord.Interaction, item: str):
    """
    Buy an item from the shop!
    """
    color = red
    if item in self.bot.dbo["others"]["shop_items"]:
      if item in self.bot.db["economy"][str(itx.user.id)]["bought_from_shop"]:
        msg = f"You have already bought this item from the shop! \nUse `{prefix}shop` to check out your shop offers again."
      else:
        cost = self.bot.dbo["others"]["shop_items"][item]
        if cost > self.bot.db["economy"][str(itx.user.id)]["golden_ticket"]:
          msg = f"You don't have enough money to buy this item! \nYou need **{cost} {ticket}** to buy it."
        else:
          if item.split(" ")[1] == "global" and self.bot.dbo["others"]["global_income_boost"] == {}:
            self.bot.db["economy"][str(itx.user.id)]["golden_ticket"] -= cost
            self.bot.db["economy"][str(itx.user.id)]["bought_from_shop"].append(item)
            await buy_item(itx, item)
            msg = f"You have bought **{item}** from the shop! \nUse `{prefix}shop` to check out your shop offers again."
            color = green
          else:
            msg = "There is already a global income boost active! Wait until the boost finishes before buying another global boost!"
    else:
      msg = f"That item is not available! \nUse `{prefix}shop` to check out your shop offers again."
    embed = discord.Embed(
      title = "Shop Purchase",
      description = msg,
      color = color
    )
    await itx.response.send_message(embed=embed)

  @buy.autocomplete("item")
  async def ac_buy_callback(self, itx: discord.Interaction, content: str):
    items = self.bot.dbo["others"]["shop_items"]
    return [Choice(name=item, value=item) for item in items]
    
  # View boosts
  @app_commands.command(name="boosts")
  @factory_check()
  async def boosts(self, itx: discord.Interaction):
    """
    View your active boosts!
    """
    msg = ""
    boosts = self.bot.db["economy"][str(itx.user.id)]["boosts"].copy()
    boosts["global"] = [self.bot.dbo["others"]["global_income_boost"]]
    # boosts = {"income": [{mult: duration}, {x: y}], "xp": [{x: y}]}
    for type_ in boosts:
      msg += f"\n**{type_.title()}: ** \n" # boosts[type_] = [{mult: duration}, {x: y}]
      if boosts[type_] in ([], [{}]):
        msg += f"You do not have any active boosts! \n"
      else:
        for boost in boosts[type_]: # boosts[type_][boost] = {mult: duration}
          msg += f"- **{list(boost.keys())[0]}x** boost ends in **{list(boost.values())[0]} hour(s)** \n"
      

    embed = discord.Embed(
      title = "Active Boosts",
      description = msg,
      color = blurple
    )
    await itx.response.send_message(embed=embed)

  # Balance Command
  @app_commands.command(name="balance")
  @factory_check()
  async def balance(self, itx: discord.Interaction, user: discord.Member = None):
    """View a user's balance or your own!"""
    if user is None:
      user = itx.user
    balance = self.bot.db["economy"][str(user.id)]["balance"]
    income = self.bot.db["economy"][str(user.id)]["income"]
    msg = f"Balance: **{balance:,}{coin}** \nIncome: **{income} {coin} / hr**"
    embed = discord.Embed(title = f"{user.name}'s balance", description = msg, color = green)
    await itx.response.send_message(embed = embed)

  # Stats Command 
  @factory_check()
  @app_commands.command(name = "stats")
  async def stats(self, itx: discord.Interaction, user: discord.Member = None):
    """View someone's stats!"""
    await get_stats(itx, user)

  @factory_check()
  @app_commands.command(name = "daily")
  async def daily(self, itx: discord.Interaction):
    """Collect your daily reward! """
    await get_daily(itx)

  @factory_check()
  @app_commands.command(name = "weekly")
  async def weekly(self, itx: discord.Interaction):
    """Collect your weekly reward!"""
    if self.bot.db["economy"][str(itx.user.id)]["levels"]["level"] >= 20:
      income = self.bot.db["economy"][str(itx.user.id)]["income"]
      balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
      last_weekly = self.bot.db["economy"][str(itx.user.id)]["last_weekly"]
      currenttime = int(time.time())
      weekly_coins = income * 12

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
      msg, color = f"This command is for users above level 20!", red
    embed = discord.Embed(title = "Weekly Reward", description = msg, color = color)
    await itx.response.send_message(embed = embed)

  @factory_check()
  @app_commands.command(name = "monthly")
  async def monthly(self, itx: discord.Interaction):
    """Collect your monthly reward!"""
    income = self.bot.db["economy"][str(itx.user.id)]["income"]
    balance = self.bot.db["economy"][str(itx.user.id)]["balance"]
    last_monthly = self.bot.db["economy"][str(itx.user.id)]["last_monthly"]
    currenttime = int(time.time())
    monthly_coins = income*24*5

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
  async def quests(self, itx: discord.Interaction):
    """View your daily quests here!"""
    await get_quests(itx)

  # Leaderboards
  @factory_check()
  @app_commands.command(name = "leaderboard")
  async def leaderboard(self, itx: discord.Interaction, type: Optional[Literal["balance", "levels", "bugs", "sponsors"]]="balance"):
    """View the various leaderboards here!"""
    note = ""
    lb_dump = {}
    for user in self.bot.db["economy"]:
      if type == "balance":
        lb_dump[user] = self.bot.db["economy"][user]["balance"]
        emoji = coin
        note = f"There are currently `{len(self.bot.db['economy'])}` users producing chocolates!"
      elif type == "bugs": 
        lb_dump[user] = self.bot.db["economy"][user]["bugs_found"]
        emoji = ":bug:"
        count = 0
        for user in self.bot.dbo['others']['bugs']:
          count += self.bot.dbo['others']['bugs'][user]
        note = f"A total of `{count}` bugs have been reported!"
      elif type == "sponsors":
        lb_dump[user] = self.bot.db["economy"][user]["sponsor"]
        emoji = ":moneybag:"
        count = 0
        for user in self.bot.db["economy"]:
          count += self.bot.db["economy"][user]["sponsor"]
        note = f"A total of **{count:,} {coin}** has been sponsored!"
      elif type == "levels":
        lb_dump[user] = self.bot.db["economy"][user]["levels"]["level"]
        emoji = " levels placeholder"
        note = f"There are currently `{len(self.bot.db['economy'])}` users producing chocolates!"
        
    lb = {users: balance for users, balance in reversed(sorted(lb_dump.items(), key=lambda item: item[1]))}
    
    count = 1
    msg = ""
    for user in lb:
      level = self.bot.db["economy"][user]["levels"]["level"]
      fire = ":fire:" if level >= 100 else ""
      custom_emoji = custom_emojis[user] if user in custom_emojis else ""
      tag = f"**{custom_emoji}{fire} [{level}]**"
        
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
    """Redeem your CocoaBot code here!"""
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
    """Open some chests!"""
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
          
async def setup(bot):
  await bot.add_cog(Economy(bot))