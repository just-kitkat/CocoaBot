import discord, time, random, math, asyncio
from vars import *
from utils import *
from errors import *
from discord import app_commands
from typing import Literal, Optional
from datetime import timedelta
from discord.ext import commands
from discord.app_commands import Choice
from PIL import ImageFont, ImageDraw, Image
from pilmoji import Pilmoji

    
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
      """
      if reward[5:].startswith("Worker"): amt = "workers"
      if reward[5:].startswith("Machine"): amt = "machine_level"
      itx.client.db["economy"][str(itx.user.id)][amt] += 1
      msg = f"Your **{amt.replace('_', ' ')}** has increased by 1"
      """
      msg = "This reward has been disabled. reward: " + reward

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
    """Start your chocolate journey here!"""
    if str(itx.user.id) not in self.bot.db["economy"]:
      self.bot.db["economy"][str(itx.user.id)] = {
        "balance": 10 , "last_sold": int(time.time()), 
        "last_daily": 1, "last_weekly": 1, "last_monthly": 1, "daily_streak": 0, 
        "prestige": 0, "kitkats_sold": 0, "last_cf": 1, 
        "sponsor": 0, "diamonds": 0, "kitkats_boost": 0, "income": 100, 
        "unlocked_upgrades": ["farm"],
        "levels": {"xp" : 0, "xp_mult" : 1, "level" : 1, "xp_needed" : 20}, 
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
          }
        }, 
        "fish": {
          "last_fish": 0, "rod_level": 1, "tuna": 0, "grouper": 0, "snapper": 0, "salmon": 0, "cod": 0
        }, 
        "pets": {
          "name": "", "type": "", "tier": 0, "level": 0, "last_hunt": 1, "last_feed": 1, "last_play": 1, "food": 0
        },
        "quest": {
          "fish": {"name": "tuna", "times": 5, "completed": False},
          "hunt": {"times": 1, "times_completed": 0, "completed": False}
        },
        "games": {
          "sliding_puzzle_8_moves": -1, "sliding_puzzle_8_time": -1
        }
      }
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

    income = self.bot.db["economy"][str(itx.user.id)]["income"]
    embed = discord.Embed(
      title = "**The kitkat factory guide!**", 
      description = f"""
Hello {itx.user.mention}, it looks like you are lost! Do not worry, `?guide` will always be avaliable to you! 

Currently, you are producing kitkats at a rate of `{income} {coin} / hour`! To sell the kitkats, all you need to do is `{self.bot.prefix}sell`! 
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
  
      income = self.bot.db["economy"][str(itx.user.id)]["income"]
      amt_sold = random.randint(income//10, income)
  
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
    await get_fish(itx)
        
  # Upgrades Command
  @factory_check()
  @is_owner()
  @app_commands.command(name = "upgrade")
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
    ]
  )
  async def upgrade(self, itx: discord.Interaction, name: Optional[str]=None):
    """Upgrades!!!"""
    await get_upgrade(itx, name)
        

  # Balance Command
  @app_commands.command(name = "balance")
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
  @app_commands.command(name = "statistics")
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
    if self.bot.db["economy"][str(itx.user.id)]["prestige"] >= 1:
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
      msg, color = f"This is a prestige 1 feature! Do `{self.bot.prefix}prestige` to view prestige costs!", red
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
  @is_owner()
  async def quests(self, itx: discord.Interaction):
    """View your daily quests here!"""
    await get_quests(itx)
        

  @factory_check()
  @app_commands.command(name = "prestige")
  async def prestige(self, itx: discord.Interaction):
    """View the hall of prestiges!"""
    await itx.response.send_message("This command has been disabled!")
    return
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
      self.bot.db["economy"][str(itx.user.id)]["balance"] = 0
      self.bot.db["economy"][str(itx.user.id)]["last_sold"] = int(time.time())
      self.bot.db["economy"][str(itx.user.id)]["income"] = 100
      self.bot.db["economy"][str(itx.user.id)]["last_daily"] = 1
      self.bot.db["economy"][str(itx.user.id)]["last_weekly"] = 1
      self.bot.db["economy"][str(itx.user.id)]["last_monthly"] = 1
      self.bot.db["economy"][str(itx.user.id)]["prestige"] += 1
      self.bot.db["economy"][str(itx.user.id)]["fish"] = {"last_fish": 0, "rod_level": 1, "tuna": 0, "grouper": 0, "snapper": 0, "salmon": 0, "cod": 0}
      self.bot.db["economy"][str(itx.user.id)]["pets"] = {"name": "", "type": "", "tier": 0, "level": 0, "last_hunt": 1, "food": 0, "last_feed": 0, "last_play": 0}
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