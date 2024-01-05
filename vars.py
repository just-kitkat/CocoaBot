import time
import discord
import asyncio

bot_name = "CocoaBot"
owner = 915156033192734760
owner_username = ".justkitkat"

cross = "❌"
tick = "✅"
coin = "🪙"
choco = "🍫"
ticket = "<:golden_ticket:1036538363139850270>"
prefix = "/"
red_square, yellow_square, green_square = "🟥", "🟨", "🟩"
trashcan = "🗑️"
recipe_fragment = "📃"
diamond = "<:diamond:1017435757616570409>"

server_voter_role = 1027762825059381308
xp_needed_base = 10
unix_day = 1661788800
eco_prestige = [0, 1000000, 2500000, 5000000, 10000000, 20000000]
lottery_channel = 924492712328171530
restart_log_channel = 927434363317157899
log_channel = 923029963580518431
custom_emojis = {
  "726965815265722390" : "<:trolllol:944407059443617792>"
}

shop_info = {
  "tickets": {
    "1.5x personal income boost (12h)" : 5, 
    "2x personal income boost (12h)" : 8, 
    "4x personal income boost (12h)" : 15, 
    "2x personal income boost (1d)" : 15, 
    "2x personal income boost (3d)" : 35, 
    "1.5x global income boost (1d)" : 20, 
    "1.5x global income boost (3d)" : 50, 
    "2x global income boost (1d)" : 50, 
    "1.5x personal XP boost (6h)" : 20, 
    "1.5x personal XP boost (12h)" : 36, 
    "1.5x personal XP boost (1d)" : 70, 
    "2x personal XP boost (12h)" : 40, 
    "2x personal XP boost (2d)" : 100, 
    f"20 {diamond}" : 8, 
    f"10 {diamond}" : 4, 
    f"100 {diamond}" : 40, 
    f"1,000,000 {coin}" : 20, 
  }
}

fish_values = {
  "tuna": 100,
  "grouper": 500,
  "snapper": 2500,
  "salmon": 25_000,
  "cod": 250_000
}
chest_rewards = {
      "normal": {
        "common": ["Small Bag of Coins", "5x Pet Food", "Small Bag of Fish", f"6 {diamond}"],
        "rare": ["Medium Bag of Coins", "10x Pet Food", f"8 {diamond}", f"1 {ticket}"],
        "legendary": ["Large Bag of Coins", "20x Pet Food", "Medium Bag of Fish", "2% Income Multiplier", f"3 {ticket}", f"12 {diamond}"]
      },
      "rare": {
        "common": ["Medium Bag of Coins", "8x Pet Food", "Small Bag of Fish", "2% income Multiplier", f"20 {diamond}"],
        "rare": ["Large Bag of Coins", "15x Pet Food", "Medium Bag of Fish", f"30 {diamond}", f"2 {ticket}"],
        "legendary": ["Cart Full of Coins", "20x Pet Food", f"69 {diamond}", "5% Income Multiplier", f"5 {ticket}"]
      },
      "legendary": {
        "common": ["Large Bag of Coins", "20x Pet Food", "Medium Bag of Fish", f"69 {diamond}", "2% Income Multiplier", f"3 {ticket}"],
        "rare": ["Cart Full of Coins", "40x Pet Food", "Large Bag of Fish", f"250 {diamond}", "6% Income Multiplier", f"5 {ticket}"],
        "legendary": ["House Full of Coins", "100x Pet Food", f"500 {diamond}", "10% Income Multiplier", f"8 {ticket}"]
      }
    }

tips = [
  f"Earn tickets from quests, chests and leveling up rewards! You can spend them in `{prefix}shop`",
  f"Buy xp and income boosts in `{prefix}shop`!",
  f"You get income every hour! Spend it wisely!",
  f"Remember to vote for our {bot_name} discord server before running `{prefix}daily` to get double rewards!",
  f"View your current boosts using `{prefix}boosts`",
  f"Unlock different locations to increase upgrades and multipliers!",
  f"Complete all 3 daily quests to get a {ticket}",
  f"Join our support server for lotteries, giveaways and many more!"
]

whitespace = "\u200b"
is_ready = False
online_since = int(time.time())
red, green, blurple = discord.Color.red(), discord.Color.green(), discord.Color.blurple()
disc_invite = "https://discord.gg/PmAbwpCqDD"
bot_invite = "https://discord.com/api/oauth2/authorize?client_id=919773782451830825&permissions=277092781120&scope=bot%20applications.commands"
server_vote = "https://top.gg/servers/923013388966166528"
bot_vote = "https://top.gg/bot/919773782451830825"
adv_msg = f"Useful Links: [Invite me]({bot_invite}) | [Support server]({disc_invite}) | [Vote for me]({bot_vote})"

# 947474270991310891

