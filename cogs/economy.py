import discord, time, random, math, asyncio
from vars import *
from errors import *
from datetime import timedelta, date, datetime
from discord.ext import commands

class Economy(commands.Cog, name = "General Commands"):

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def start(self, ctx):
    if str(ctx.author.id) not in self.bot.db["economy"]:
      self.bot.db["economy"][str(ctx.author.id)] = {"balance" : 10 , "last_sold" : int(time.time()), "workers" : 1, "machine_level" : 1, "storage" : 200, "last_daily" : 1, "last_weekly" : 1, "last_monthly" : 1, "prestige" : 0, "kitkats_sold" : 0, "last_cf": 1, "upgrade_cap" : 10, "sponsor" : 0, "chests" : 0, "fish" : {"last_fish" : 0, "rod_level" : 1}, "pets" : {"name": "", "type": "", "tier" : 0, "level": 0, "last_hunt" : 1}, "daily_streak" : 0}
      embed = discord.Embed(
        title = "**Kitkat Factory**", 
        description = f"""
  Hello {ctx.author.mention}, you have successfully built a factory! Welcome to your very own **Kitkat Factory!** 
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
      await ctx.reply(embed = embed, mention_author = False)
    else:
      await ctx.reply(f"You already own a factory! Do `{self.bot.prefix}help economy` to see the commands you can use!", mention_author = False)

  @factory_check()
  @commands.command(aliases = ["tutorial"])
  async def guide(self, ctx):
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]

    rate_of_kitkats = (workers + 2) * machine_lvl
    embed = discord.Embed(
      title = "**The kitkat factory guide!**", 
      description = f"""
Hello {ctx.author.mention}, it looks like you are lost! Do not worry, `?guide` will always be avaliable to you! 

Currently, you are producing kitkats at a rate of `{rate_of_kitkats} {choco} / minute`! To sell the kitkats, all you need to do is `{self.bot.prefix}sell`! 
Making upgrades to your factory will increase your kitkats' value!
Current kitkat value: **2 {coin} / kitkat**.
      
To produce kitkats at a faster rate, you can either hire more workers or upgrade your machine! You can do `{self.bot.prefix}upgrades` for more information on that! To view your balance, you can do `{self.bot.prefix}balance`.
You can also get your own pet by doing `{self.bot.prefix}pet`! Having a pet gives you access to the `{self.bot.prefix}hunt` command, which gives you a random amount of coins every hour!

You can view the leaderboard using `{self.bot.prefix}leaderboard` and prestige using `{self.bot.prefix}prestige`. To join giveaways, lotteries and more, you can join KitkatBot's official server by clicking [here](https://discord.gg/hhVwjFBJ2C)! Remember to do `{self.bot.prefix}daily` everyday to claim a free gift, good luck!
""", 
      color = discord.Color.green()
    )
    await ctx.reply(embed = embed, mention_author = False)

  @factory_check()
  @commands.command(aliases = ["s"])
  async def sell(self, ctx):
    last_sold = self.bot.db["economy"][str(ctx.author.id)]["last_sold"]
    time_diff = int(time.time()) - last_sold
    
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
    storage = self.bot.db["economy"][str(ctx.author.id)]["storage"]

    rate_of_kitkats = (workers + 2) * machine_lvl
    amt_sold = math.floor(time_diff / 60) * rate_of_kitkats

    if math.floor(amt_sold) <= 0:
      await ctx.reply(f"You currently have no kitkats to sell! You are currently producing `{str(rate_of_kitkats)}{choco} / minute`")
    else:
      if math.floor(amt_sold) > self.bot.db["economy"][str(ctx.author.id)]["storage"]:
        amt_sold_final = self.bot.db["economy"][str(ctx.author.id)]["storage"]
        self.bot.db["economy"][str(ctx.author.id)]["balance"] += math.floor(amt_sold_final) * 2
        self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(time.time())
        self.bot.db["economy"][str(ctx.author.id)]["kitkats_sold"] += math.floor(amt_sold_final)
        if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 4:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] += (math.floor(amt_sold_final * 2/100*10))
          self.bot.db["economy"][str(ctx.author.id)]["kitkats_sold"] += math.floor(amt_sold_final/100*10)
          msg = f"You have sold {amt_sold_final}{choco} and have earned **{amt_sold_final * 2} {coin}** and an extra **{(math.floor(amt_sold_final * 2/100*5))}{coin}** as a prestige bonus! (`+5%`). You could have made more kitkats but your storage capacity could only hold **{storage}{choco}!** "
        elif self.bot.db["economy"][str(ctx.author.id)]["prestige"] < 4:
          
          msg = f"You have sold {amt_sold_final}{choco} and have earned **{amt_sold_final * 2} {coin}!** You could have made more kitkats but your storage capacity could only hold **{storage}{choco}!** Upgrade your storage capacity using `{self.bot.prefix}upgrade storage`."
      else:
        if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 4:
          amt_sold_final = amt_sold
          self.bot.db["economy"][str(ctx.author.id)]["balance"] += math.floor(amt_sold_final) * 2
          self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(time.time())
          self.bot.db["economy"][str(ctx.author.id)]["balance"] += (math.floor(amt_sold_final * 2/100*5))
          self.bot.db["economy"][str(ctx.author.id)]["kitkats_sold"] += math.floor(amt_sold_final/100*5)
          msg = f"You have sold {amt_sold_final}{choco} and have earned **{amt_sold_final * 2} {coin}** and an extra **{(math.floor(amt_sold_final * 2/100*5))}{coin}** as a prestige bonus! (`+5%`)." 
        elif self.bot.db["economy"][str(ctx.author.id)]["prestige"] < 4:
          amt_sold_final = amt_sold
          self.bot.db["economy"][str(ctx.author.id)]["balance"] += math.floor(amt_sold_final * 2)
          self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(time.time())
          self.bot.db["economy"][str(ctx.author.id)]["kitkats_sold"] += math.floor(amt_sold_final)
          msg = f"You have sold {amt_sold_final}{choco} and have earned **{math.floor(amt_sold_final * 2)} {coin}**! "
      
      msg += f"You are currently producing `{str(rate_of_kitkats)}{choco} / minute`"
      await ctx.reply(msg, mention_author = False)
  
  @commands.command(aliases = ["f"])
  async def fish(self, ctx):
    """Take a break and go fishing!"""
    if str(ctx.author.id) in self.bot.db["economy"]:
      level = self.bot.db["economy"][str(ctx.author.id)]["fish"]["rod_level"]
      if level == 1:
        cooldown = 300
        mins_ = 5
        money = random.randint(100, 1000)
      if level == 2:
        cooldown = 240
        mins_ = 4
        money = random.randint(300, 2000)
      if level == 3:
        cooldown = 120
        mins_ = 2
        money = random.randint(500,4000)
  
      if time.time() >= self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] + cooldown:
        luck = random.randint(1,100)
        if luck > 30:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] += money
          self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] = int(time.time())
          embed = discord.Embed(
            title = "Fishing", 
            description = f"You went fishing and caught a wallet! You got **{money}{coin}**.", 
            color = discord.Color.green()
          )
          await ctx.reply(embed = embed)
        else:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] -= money
          self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] = int(time.time())
          embed = discord.Embed(
            title = "Fishing", 
            description = f"You went fishing and fished out a scuba diver! You got fined **{money}{coin}**", 
            color = discord.Color.red()
          )
          await ctx.reply(embed = embed)
          if self.bot.db["economy"][str(ctx.author.id)]["balance"] < 0:
            self.bot.db["economy"][str(ctx.author.id)]["balance"] = 0
      elif time.time() < self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] + cooldown:
          currenttime = int(time.time())
          last_fish = self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"]
          mins_left = str(math.floor((mins_ - ((currenttime - last_fish) % 3600) / 60)))
          secs_left = str(math.floor((60 - ((currenttime - last_fish) % 3600) % 60)))
          embed = discord.Embed(
            title = "Fishing", 
            description = f"You cannot fish so soon! You can fish again in `{mins_left}m {secs_left}s`", 
            color = discord.Color.orange()
          )
          await ctx.reply(embed = embed)
    else:
      await ctx.reply(f"Whoops, looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!")

  # Upgrades Command
  @factory_check()
  @commands.command(aliases = ["upgrade", "up", "shop"])
  async def upgrades(self, ctx, *, name = None):
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
    storage = self.bot.db["economy"][str(ctx.author.id)]["storage"]
    total_upgrades = workers + machine_lvl
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    upgrade_cap = self.bot.db["economy"][str(ctx.author.id)]["upgrade_cap"]
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
    rod_level = self.bot.db["economy"][str(ctx.author.id)]["fish"]["rod_level"]
    if rod_level < 3:
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
Storage capacity: **{storage}**
Command: `{self.bot.prefix}upgrade storage`

Fishing Rod Upgrade: **{rod_upgrade}**
FIshing Rod level: **{rod_level}**
Command: `{self.bot.prefix}upgrade rod`

To upgrade your pet, you can use `{self.bot.prefix}pet upgrade`.

Current balance: **{balance}{coin}**  |  `{rate_of_kitkats}{choco} / minute`
Do `{self.bot.prefix}help economy` to see all economy commands!
"""
      color = discord.Color.blurple()
    elif name in ("w", "worker", "workers"):
      if balance >= workers_upgrade:
        if upgrade_cap > total_upgrades:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] -= workers_upgrade
          self.bot.db["economy"][str(ctx.author.id)]["workers"] += 1
          title = "Upgrade Successful!"
          msg, color = f"You spent {workers_upgrade}{coin} to hire another worker! \n`Total workers: {workers + 1}`", green
        else:
          msg = f"Your upgrade capacity is full! Do `{self.bot.prefix}upgrade capacity` to increase it."
      else: 
        msg = f"You do not have enough coins to hire another worker! You need **{workers_upgrade - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
  
    elif name in ("s", "storage", "storages"):
      if balance >= storage_upgrade:
        self.bot.db["economy"][str(ctx.author.id)]["balance"] -= storage_upgrade
        self.bot.db["economy"][str(ctx.author.id)]["storage"] += storage * 2
        title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent {storage_upgrade}{coin} to upgrade your storage capacity! \n`Storage capacity: {storage * 2}`", green
      else: 
        msg = f"You do not have enough coins to upgrade your storage! You need **{storage_upgrade - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
  
    elif name in ("m", "machine", "machines"):
      if balance >= machine_upgrade:
        if upgrade_cap > total_upgrades:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] -= machine_upgrade
          self.bot.db["economy"][str(ctx.author.id)]["machine_level"] += 1
          title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent {machine_upgrade}{coin} to upgrade your machine! \nMachine level: `{machine_lvl + 1}`", green
        else:
          msg = f"Your upgrade capacity is full! Do `{self.bot.prefix}upgrade capacity` to increase it."
      else: 
        msg = f"You do not have enough coins to upgrade your machine! You need **{machine_upgrade - balance}{coin} more!** Do `{self.bot.prefix}help economy` to explore other commands!"
    elif name == "cap" or name == "capacity":
      if balance >= cap_upgrade:
        self.bot.db["economy"][str(ctx.author.id)]["balance"] -= cap_upgrade
        self.bot.db["economy"][str(ctx.author.id)]["upgrade_cap"] += 10
        title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent {cap_upgrade}{coin} to upgrade your upgrades capacity! \nCurrent Capacity: `{upgrade_cap + 10}`", green
      else: 
        msg = f"You do not have enough coins to upgrade your capacity! You need **{cap_upgrade - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
    elif name in ("rod", "fish", "fishing rod"):
      if rod_level < 3:
        if balance >= rod_upgrade_:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] -= rod_upgrade_
          self.bot.db["economy"][str(ctx.author.id)]["fish"]["rod_level"] += 1
          title, msg, color = "Upgrade Successful!", f"Upgrade successfull! You spent {rod_upgrade_}{coin} to upgrade your fishing rod! \nFishing rod level: `{rod_level + 1}`", green
        else: 
          msg = f"You do not have enough coins to upgrade your fishing rod! You need **{rod_upgrade_ - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!"
      else: 
        msg = "Your fishing rod is already maxed out!"
    embed = discord.Embed(title = title, description = msg, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  # Balance Command
  @factory_check()
  @commands.command(aliases = ["b", "bal"])
  async def balance(self, ctx, user: discord.Member = None):
    if user is None:
      user = ctx.author
    balance = self.bot.db["economy"][str(user.id)]["balance"]
    bal = f"{balance:,}"
    if user == ctx.author:
      msg = f"Your balance is **{bal}{coin}**! \nYou can do `{self.bot.prefix}sell` to sell your current kitkats and earn more money!"
    else:
      msg = f"**{user.name}'s** balance is **{bal}{coin}!**"
    embed = discord.Embed(title = f"{user.name}'s balance", description = msg, color = green)
    await ctx.send(embed = embed, mention_author = False)

  # Stats Command
  @factory_check()
  @commands.command(aliases = ["stat", "profile", "statistics"])
  async def stats(self, ctx, user: discord.Member = None):
    if user is None:
      user = self.bot.get_user(ctx.author.id)
    embed = discord.Embed(
      title = f"{user.name}'s profile:",
      description = f"Getting {user.name}'s statistics...", 
      color = discord.Color.blue()
    )
    embed.set_footer(text = f"Do {self.bot.prefix}profile <@user> to check someone's profile!")

    profile = await ctx.reply(embed = embed, mention_author = False)
    workers = self.bot.db["economy"][str(user.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(user.id)]["machine_level"]
    upgrade_cap = self.bot.db["economy"][str(user.id)]["upgrade_cap"]
    storage = self.bot.db["economy"][str(user.id)]["storage"]
    rate_of_kitkats = (workers + 2) * machine_lvl
    balance = self.bot.db["economy"][str(user.id)]["balance"]
    kitkats_sold = self.bot.db["economy"][str(user.id)]["kitkats_sold"]
    prestige = self.bot.db["economy"][str(user.id)]["prestige"]
    rod_level = self.bot.db["economy"][str(user.id)]["fish"]["rod_level"]
    daily_streak = self.bot.db["economy"][str(user.id)]["daily_streak"]
    msg = f"""
Balance: **{balance}{coin}** | `{rate_of_kitkats}{choco} / minute`

Machine Level: `{machine_lvl}`
Workers: `{workers}`
Upgrade Capacity: `{upgrade_cap}`
Kitkat Storage: `{storage}`
Fishing Rod Level: `{rod_level}`
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
    await profile.edit(embed = new_embed)

  @factory_check()
  @commands.command(aliases = ["d"])
  async def daily(self, ctx):
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    last_daily = self.bot.db["economy"][str(ctx.author.id)]["last_daily"]
    currenttime = int(time.time())
    rate_of_kitkats = (workers + 2) * machine_lvl
    daily_coins = int(rate_of_kitkats) * 100
    daily_streak = self.bot.db["economy"][str(ctx.author.id)]["daily_streak"]
    
    if currenttime >= (last_daily + 86400):
      pres_coins = 0
      streak_bonus = 500
      if currenttime >= (last_daily + 86400*2):
        self.bot.db["economy"][str(ctx.author.id)]["daily_streak"] = 0
        streak_coins = 0
      else:
        self.bot.db["economy"][str(ctx.author.id)]["daily_streak"] += 1
      streak_coins = self.bot.db["economy"][str(ctx.author.id)]["daily_streak"] * streak_bonus
        
      daily_streak = self.bot.db["economy"][str(ctx.author.id)]["daily_streak"]
      if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 2:
        pres_coins = math.floor(daily_coins/100*15)
        rate = "15%"
        if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 3:
          pres_coins = math.floor(daily_coins/100*30)
          rate = "30%"
      total_coins = daily_coins + pres_coins + streak_coins

      self.bot.db["economy"][str(ctx.author.id)]["last_daily"] = time.time()
      self.bot.db["economy"][str(ctx.author.id)]["balance"] += total_coins
      updated_bal = balance + total_coins
      if self.bot.db["economy"][str(ctx.author.id)]["prestige"] < 2:
        msg = f"Daily reward: **{daily_coins}{coin}** \nStreak Bonus: **{streak_coins}{coin}** \nTotal Reward: **{total_coins}{coin}** \n\nCurrent Balance: **{updated_bal}{coin}** \nDaily Streak: `{daily_streak}` "
      else: 
        msg, color = f"Daily reward: **{daily_coins}{coin}** \nPrestige bonus: **{pres_coins}{coin}** (+{rate}) \nStreak Bonus: **{streak_coins}{coin}** \nTotal Reward: **{total_coins}{coin}** \n\nCurrent Balance: **{updated_bal}{coin}** \nDaily Streak: `{daily_streak}` ", green
      
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
    await ctx.reply(embed = embed, mention_author = False)

  @factory_check()
  @commands.command(aliases = ["w"])
  async def weekly(self, ctx):
    if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 1:
      workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
      machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
      balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
      last_weekly = self.bot.db["economy"][str(ctx.author.id)]["last_weekly"]
      currenttime = int(time.time())
      rate_of_kitkats = (workers + 2) * machine_lvl
      weekly_coins = (int(rate_of_kitkats) + 20) * 800

      if currenttime >= (last_weekly + 604800):
        self.bot.db["economy"][str(ctx.author.id)]["last_weekly"] = int(time.time())
        self.bot.db["economy"][str(ctx.author.id)]["balance"] += weekly_coins
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
    await ctx.reply(embed = embed, mention_author = False)

  @factory_check()
  @commands.command(aliases = ["m"])
  async def monthly(self, ctx):
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    last_monthly = self.bot.db["economy"][str(ctx.author.id)]["last_monthly"]
    currenttime = int(time.time())
    rate_of_kitkats = (workers + 2) * machine_lvl
    monthly_coins = (int(rate_of_kitkats) + 20) * 2000

    if currenttime >= (last_monthly + 2592000):
      self.bot.db["economy"][str(ctx.author.id)]["last_monthly"] = time.time()
      self.bot.db["economy"][str(ctx.author.id)]["balance"] += monthly_coins
      msg, color = f"You have claimed your monthly gift of **{monthly_coins}{coin}!** \nCurrent balance: **{balance + monthly_coins}{coin}**", green
    else:
      td = timedelta(seconds=2592000-currenttime+last_monthly)
      days_left = td.days
      hours_left = td.seconds // 3600
      mins_left = (td.seconds % 3600) // 60
      secs_left = td.seconds % 60
      msg, color = f"You can claim your monthly gift in `{days_left}d {hours_left}h {mins_left}m {secs_left}s`. ", red
    embed = discord.Embed(title = "Monothly Reward", description = msg, color = color)
    await ctx.reply(embed = embed, mention_author = False)

  @factory_check()
  @commands.command(aliases = ["p", "pres"])
  async def prestige(self, ctx):
    prestige = self.bot.db["economy"][str(ctx.author.id)]["prestige"]
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    
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
        prestige_msg += f"\nYou have enough coins to prestige! React with a :white_check_mark: to prestige! \n**WARNING:** This will reset ALL your progress!"
    elif prestige == 5:
      prestige_msg += f"\nYou are currently at the highest prestige level and cannot prestige anymore!"
    else:
      prestige_msg += f"You do not have enough coins to prestige! Coins needed: **{eco_prestige[prestige + 1]}{coin}**"

    embed = discord.Embed(
      title = "Prestige", 
      description = prestige_msg, 
        colour = discord.Color.blue()
        )
    prestige_confirm = await ctx.send(embed = embed)
    if prestige < 5:
      if balance >= eco_prestige[prestige + 1]:
        await prestige_confirm.add_reaction("✅")
  
        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == prestige_confirm and str(reaction.emoji) in ["✅"]
        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=60,
                                                check=check)
            if str(reaction.emoji) == "✅" and self.bot.db["economy"][str(ctx.author.id)]["balance"] >= eco_prestige[prestige + 1]:
                self.bot.db["economy"][str(ctx.author.id)]["balance"] = 0
                self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(time.time())
                self.bot.db["economy"][str(ctx.author.id)]["workers"] = 1
                self.bot.db["economy"][str(ctx.author.id)]["machine_level"] = 1
                self.bot.db["economy"][str(ctx.author.id)]["storage"] = 200
                self.bot.db["economy"][str(ctx.author.id)]["upgrade_cap"] = 10
                self.bot.db["economy"][str(ctx.author.id)]["last_daily"] = 1
                self.bot.db["economy"][str(ctx.author.id)]["last_weekly"] = 1
                self.bot.db["economy"][str(ctx.author.id)]["last_monthly"] = 1
                self.bot.db["economy"][str(ctx.author.id)]["prestige"] += 1
                self.bot.db["economy"][str(ctx.author.id)]["fish"] = {"last_fish" : 1, "rod_level" : 1}
                self.bot.db["economy"][str(ctx.author.id)]["pets"] = {"name": "", "type": "", "tier" : 0, "level": 0, "last_hunt" : 1}
                self.bot.db["economy"][str(ctx.author.id)]["daily_streak"] = 0
                  
                new_embed = discord.Embed(
                    title=f"Prestige",
                    description=f"You have successfully prestiged! **Prestige level: {prestige + 1}**",
                    color=discord.Color.green())
                await prestige_confirm.edit(embed=new_embed)
                p = self.bot.db["economy"][str(ctx.author.id)]["prestige"]
                channel = bot.get_guild(923013388966166528).get_channel(971043716083089488)
                await channel.send(f"**{ctx.author} has just prestiged! `Prestige {prestige} > {p}` [{ctx.author.id}]**")
  
        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time.")

  @factory_check()
  @commands.command(aliases = ["lb", "leaderboards"])
  async def leaderboard(self, ctx, arg = "kitkats"):
    note = ""
    lb_dump = {}
    arg = arg.lower()
    for user in self.bot.db["economy"]:
      if arg in ("c", "coin", "coins", "bal", "balance"):
        lb_dump[user] = self.bot.db["economy"][user]["balance"]
        emoji = coin
        note = f"There are currently `{len(self.bot.db['economy'])}` users producing kitkats!"
        
      elif arg in ("b", "bug", "bugs"):
        try:
          lb_dump[user] = self.bot.dbo["others"]["bugs"][user]
        except: 
          pass
        emoji = ":bug:"
        count = 0
        for user in self.bot.dbo['others']['bugs']:
          count += self.bot.dbo['others']['bugs'][user]
        note = f"A total of `{count}` bugs have been reported!"
        
      elif arg in ("s", "sponsor", "sponsors"):
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
    await ctx.send(embed = embed)

  @factory_check()
  @commands.command()
  async def redeem(self, ctx, code = None):
    if code in self.bot.dbo["others"]["code"] and code is not None and str(ctx.author.id) in self.bot.db["economy"]:
      money = self.bot.dbo["others"]["code"][code]
      self.bot.dbo["others"]["code"].pop(code)
      self.bot.db["economy"][str(ctx.author.id)]["balance"] += money
      embed = discord.Embed(
        title = "Code claimed!",
        description = f"You have successfully claimed the code `{code}`. \nYou have earned **{money} {coin}**",
        color = discord.Color.blurple()
      )
      await ctx.reply(embed = embed, mention_author = False)
      channel = bot.get_guild(923013388966166528).get_channel(968460468505153616)
      embed = discord.Embed(title = f"{ctx.author} has claimed a code.", description = f"Code: `{code}` \nAmount: **{money} {coin}**", color = discord.Color.blurple())
      await channel.send(embed = embed)
    elif str(ctx.author.id) not in self.bot.db["economy"]:
      raise FactoryCheck(f"Looks like you do not own a factory! Do `{self.bot.prefix}start` to build one!")
    else:
      embed = discord.Embed(
        title = "Code not found...",
        description = f"This code has been redeemed before or does not exist... Sorry.",
        color = discord.Color.red()
      )
      await ctx.reply(embed = embed, mention_author = False)

  @commands.command()
  async def totalkitkats(self, ctx):
    total = 0
    for user in self.bot.db["economy"]:
      total += self.bot.db["economy"][user]["kitkats_sold"]
    kitkats = f"{total:,}"
    await ctx.reply(f"A total of **{kitkats}{choco}** has been made!")
    
async def setup(bot):
  await bot.add_cog(Economy(bot))