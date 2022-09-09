import time, discord

bot_name = "KitkatBot"

cross = "❌"
tick = "✅"
coin = ":coin:"
choco = "🍫"
trashcan = "🗑️"
diamond = "<:diamond:1017435757616570409>"
unix_day = 1661788800
eco_prestige = [0, 1000000, 2500000, 5000000, 10000000, 20000000]
custom_emojis = {
  "726965815265722390" : "<:trolllol:944407059443617792>"
}
fish_values = {
  "tuna": 100,
  "grouper": 500,
  "snapper": 2500,
  "salmon": 250000,
  "cod": 1000000
}
chest_rewards = {
      "normal": {
        "common": ["Small Bag of Coins", "5x Pet Food", "Small Bag of Fish"],
        "rare": ["Medium Bag of Coins", "10x Pet Food", f"2 {diamond}"],
        "legendary": ["Large Bag of Coins", "Free Worker Upgrade", "20x Pet Food", "Medium Bag of Fish"]
      },
      "rare": {
        "common": ["Medium Bag of Coins", "8x Pet Food", "Small Bag of Fish"],
        "rare": ["Large Bag of Coins", "15x Pet Food", "Free Worker Upgrade", "Medium Bag of Fish", f"20 {diamond}"],
        "legendary": ["Cart Full of Coins", "Free Machine Upgrade", "20x Pet Food", f"69 {diamond}"]
      },
      "legendary": {
        "common": ["Large Bag of Coins", "20x Pet Food", "Medium Bag of Fish", "Free Worker Upgrade", f"69 {diamond}"],
        "rare": ["Cart Full of Coins", "40x Pet Food", "Free Machine Upgrade", "Large Bag of Fish", f"250 {diamond}"],
        "legendary": ["House Full of Coins", "100x Pet Food", f"500 {diamond}"]
      }
    }
prestige_icons = ["0", "I", "II", "III", "IV", "V"]
whitespace = "\u200b"
is_ready = False
online_since = int(time.time())
red, green, blurple = discord.Color.red(), discord.Color.green(), discord.Color.blurple()
sinvite = "None"
binvite = "None"
adv_msg = f"Useful Links: [Invite me]({binvite}) | [Support server]({sinvite})" # Voting link not yet

# 947474270991310891