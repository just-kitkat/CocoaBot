# Keeps bot from going offline
import keep_alive

keep_alive.keep_alive()
# return user == ctx.author and str(reaction.emoji) in ["✅"]
# Import Modules
db = {}
dbo = {}
import os
import sys
import discord
import random
import requests
import json
from discord.ext import commands
from discord.ext.commands import MissingPermissions
#from replit import self.bot.db
os.system('pip install "pymongo[srv]"')
import pymongo
from pymongo import MongoClient
import asyncio
import time as _time
from datetime import timedelta
import math
import traceback

# Intents
intents = discord.Intents.all()
intents.typing = True
intents.presences = True

bot = commands.Bot(prefix="?", intents=discord.Intents.all(), case_insensitive = True)
bot.remove_command("help")
prefix = self.bot.prefix

print("Connecting to MongoDB...")
pymongouser = os.getenv('mongouser')
pymongopass = os.getenv('mongopass')
cluster = pymongo.MongoClient("""mcs""") # MCS HERE
database = cluster["KitkatBot"]
collection = database["db"]
print(f"Connected! ✅")

async def save_db():
  collection.replace_one({"_id" : 36}, {"_id" : 36, "economy" : self.bot.db["economy"]})
  collection.replace_one({"_id" : 31}, {"_id" : 31, "others" : self.bot.dbo["others"]})

# Is bot online?
@bot.event
async def on_ready():
    print("Updating database...")
    global self.bot.db
    global self.bot.dbo
  
    results = collection.find({"_id" : 36})
    for result in results:
      self.bot.db = result

    results = collection.find({"_id" : 31})
    for result in results:
      self.bot.dbo = result
    print("Updated ✅")
    print("We have logged in as {0.user}".format(bot))
    guild = bot.get_guild(923013388966166528)
    log_id = guild.get_channel(927434363317157899)
    online_since = int(_time.time())
    ping = round(bot.latency * 1000)
    log_embed = discord.Embed(
      title = "KitkatBot Restarted",
      description = f"KitkatBot restarted <t:{online_since}:R>. \nPing: `{ping}ms`",
      color = discord.Color.green()
    )
    await log_id.send(embed = log_embed)
    cd = 1
    while True:
      channel = guild.get_channel(923018513008963594)
      msg_id = 926092458981478430
      msg = await channel.fetch_message(msg_id)
      updating_in = int(_time.time() + 1800)
      
      ping = round(bot.latency * 1000)
      last_pinged = int(_time.time())

      embed = discord.Embed(
      title = "KitkatBot is **ONLINE** :green_circle:",
      description = f"KitkatBot has been online since <t:{online_since}> \nKitkatBot restarted <t:{online_since}:R>\nLast pinged: <t:{last_pinged}:R> \nPing: `{ping}ms` \n\n**Note:** *If the bot was pinged over 15 minutes ago, please ping* `kitkat3141#0422`",
      color = discord.Color.green()
    )
      await msg.edit(embed = embed)

      channel = guild.get_channel(934453506432192512)
      msg_id = 934453734598139935
      lbmsg = await channel.fetch_message(msg_id)
      ecoLB = {}
      for i in self.bot.db["economy"]:
        ecoLB[i] = self.bot.db["economy"][i]["kitkats_sold"]
      if ecoLB != {}:
        top_bal = max(ecoLB.values())
        top_user = list(ecoLB.keys())[list(ecoLB.values()).index(max(ecoLB.values()))]
        guild = bot.get_guild(923013388966166528)
        user = guild.get_member(int(top_user))
        role = guild.get_role(923435838640103454)
        
        if guild.id == 923013388966166528 and len(role.members) > 1:
          for member in role.members:
            await member.remove_roles(role)
        if guild.id == 923013388966166528 and guild.get_role(923435838640103454) not in guild.get_member(int(top_user)).roles:
          for member in role.members:
            await member.remove_roles(role)
          await user.add_roles(role)
      else:
        top_user = "No one here, "
        top_bal = f"do `{self.bot.prefix}help economy` to see avaliable commands!"
      prestige_icons = ["0", "I", "II", "III", "IV", "V"]
      count = 1
      msg = ""
      if cd % 6 == 0:
        p1 = guild.get_role(923788578482421810)
        p2 = guild.get_role(926293298593796146)
        p3 = guild.get_role(927560872820346890)
        p4 = guild.get_role(929343893160472608)
        p5 = guild.get_role(934745902776741898)
        for user in self.bot.db["economy"]:
          prestige = self.bot.db["economy"][user]["prestige"]
          current_user = guild.get_member(int(user))
          if prestige > 0:
            await current_user.add_roles(p1)
          if prestige > 1:
            await current_user.add_roles(p2)
          if prestige > 2:
            await current_user.add_roles(p3)
          if prestige > 3:
            await current_user.add_roles(p4)
          if prestige > 4:
            await current_user.add_roles(p5)
      while count <= 10:
        if ecoLB != {}:
          pres_icon = prestige_icons[db["economy"][top_user]["prestige"]]
          if self.bot.db["economy"][top_user]["prestige"] >= 1:
            if self.bot.db["economy"][top_user]["prestige"] >= 5:
              msg += f"{count}. **[{pres_icon}:fire:] {bot.get_user(int(top_user))}**: **{top_bal}{choco}** \n"
            elif self.bot.db["economy"][top_user]["prestige"] < 5:
              msg += f"{count}. **[{pres_icon}] {bot.get_user(int(top_user))}**: **{top_bal}{choco}** \n"
          else: 
            msg += f"{count}. [{pres_icon}] {bot.get_user(int(top_user))}: **{top_bal}{choco}** \n"
          ecoLB.pop(str(top_user))
          if ecoLB != {}:
            top_bal = max(ecoLB.values())
            top_user = list(ecoLB.keys())[list(ecoLB.values()).index(max(ecoLB.values()))]
          elif ecoLB == {}:
            top_user = "No one here, "
            top_bal = f"do `{self.bot.prefix}help economy` to see avaliable commands!"
          count += 1
        else:
          msg += f"{count}. {top_user} {top_bal} \n"
          count +=1
      members = 0
      for a in self.bot.db["economy"]:
        members += 1
      new_embed = discord.Embed(
        title = "Kitkat Leaderboard", 
        description = msg + f"There are currently `{members}` users producing kitkats! \nLast updated <t:{int(_time.time())}:R> \nUpdating in <t:{updating_in}:R>", 
        color = discord.Color.green()
      )
      new_embed.set_footer(text = f"Use {self.bot.prefix}lb coins for coins leaderboard")
      await lbmsg.edit(embed = new_embed)
      cd += 1
      await asyncio.sleep(300)

@bot.after_invoke
async def after_invoke(ctx):
  await save_db()

#@bot.event
async def on_guild_join(guild):
  if str(guild.id) in self.bot.dbo["others"]["server_blacklists"]:
    await guild.leave()


#    channel = self.bot.db["restart_cmd"][guild.id]
#    await channel.send("Bot restarted successfully")
# Logging messages
@bot.event
async def on_message(ctx):
    blacklisted_users = self.bot.dbo["others"]["user_blacklists"]
    username = str(ctx.author.name)
    msg = str(ctx.content)
    channel = str(ctx.channel.name)
    logging_cmd = ["say", "purge"]
    if ctx.guild.id == 923013388966166528 and ctx.channel.id == 923013388966166532 and msg.startswith("?") and bot.valid:
      await ctx.reply("KitkatBot commands are blacklisted in this channel!")
      '''
    elif ctx.author.id in blacklisted_users and ctx.content.startswith("?"):
      await ctx.reply("You are blacklisted!")
      '''
    elif ctx.author.id not in blacklisted_users:
      
      await bot.process_commands(ctx)
    if not ctx.author.bot:
      print(f"{username}: {msg} ({ctx.guild.name}, {channel})")
    """if str(ctx.guild.id) in self.bot.dbo["others"]["log_channels"] and ctx.guild.get_channel(
            self.bot.dbo["others"]["log_channels"][str(ctx.guild.id)]) is not None:
        await log_cmd(ctx)"""
    if ctx.author == bot.user:
        return


@bot.event
async def logging_error(ctx, error):
    await ctx.send(str(error))



@bot.command(aliases=["slc"])
@commands.has_permissions(manage_channels=True)
async def setlogchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("Please use `?setlogchannel <#channel>`")
    else:  
        self.bot.dbo["others"]["log_channels"][str(ctx.guild.id)] = channel.id
        value = self.bot.db['log_channels'][str(ctx.guild.id)]
        embed = discord.Embed(
            title="Logs Channel",
            description=
            f"The logs channel has been set to <#{ctx.guild.get_channel(value).id}>",
            color=discord.Color.blue())
        await ctx.send(embed=embed)


@setlogchannel.error
async def slc_error(ctx, error):
    await ctx.send(str(error))


@bot.command(aliases=["rlc"])
@commands.has_permissions(manage_channels=True)
async def removelogchannel(ctx):
    del self.bot.dbo["others"]["log_channels"][str(ctx.guild.id)]
    embed = discord.Embed(
        title="Logs",
        description=f"The logs channel has been successfully removed!",
        color=discord.Color.blue())
    await ctx.send(embed=embed)


@removelogchannel.error
async def rlc_error(ctx, error):
    await ctx.send(str(error))


async def log_cmd(ctx):
    msg = str(ctx.content)
    cmd = msg[1:].split(" ")[0]
    if cmd in ("say", "purge"):
        if cmd == "say":
            message = msg[1:].split(" ")[1]
            embed = discord.Embed(
                title=f"{ctx.author} used SAY command in {ctx.channel}",
                description=f"Message: {message}",
                color=discord.Color.blue())
            embed.set_author(name=ctx.author.display_name,
                             url=ctx.author.avatar_url,
                             icon_url=ctx.author.avatar_url)
        elif cmd == "purge":
            purged = msg[1:].split(" ")[1]
            embed = discord.Embed(
                title=f"{ctx.author} used PURGE command in {ctx.channel}",
                description=f"Amount of messages purged: {purged}",
                color=discord.Color.blue())

        embed.set_author(name=ctx.author.display_name,
                         url=ctx.author.avatar_url,
                         icon_url=ctx.author.avatar_url)
        await ctx.guild.get_channel(dbo["others"]["log_channels"][str(ctx.guild.id)]
                                    ).send(embed=embed)


# Help Command
@bot.command(aliases=["help"])
async def _help(ctx, cmd=None):
    if cmd is None:
        embed = discord.Embed(
            title="**KitkatBot Commands:**",
            url="https://KitkatBot.kitkat3141.repl.co",
            description="Here is the list of all avaliable commands!",
            color=discord.Color.blue())
        embed.add_field(name="General Commands",
                        value=f"""
{self.bot.prefix}inspire - Fills you with inspiration.
{self.bot.prefix}randomint - Gives you a random number depending on your input.
{self.bot.prefix}tictactoe (ttt) - Play tictactoe with a friend!
{self.bot.prefix}suggest - Suggest something. Suggestion channel defined using **{self.bot.prefix}ssc**.

        """,
                        inline=False)
        embed.add_field(name="Economy Commands",
                        value=f"""
{self.bot.prefix}start - Build a factory!.
{self.bot.prefix}guide - View a quick guide on the economy when you are lost!
{self.bot.prefix}sell - Sells all the kitkats you have made.
{self.bot.prefix}fish - Go fishing!
{self.bot.prefix}balance - Shows you how much coins you have earned.
{self.bot.prefix}upgrades - Shows you the avaliable upgrades.
{self.bot.prefix}daily - Claim a free gift every day!
{self.bot.prefix}weekly - Claim a free gift every week!
{self.bot.prefix}monthly - Claim a free gift every month!
{self.bot.prefix}leaderboard - View the leaderbord!
{self.bot.prefix}prestige - View the various prestiges
{self.bot.prefix}pets - Buy a lovely pet to acompany you throughout your kitkat making journey!
{self.bot.prefix}coinflip - Do a coinflip! Double your bet or lose it all!
{self.bot.prefix}profile - View someone's profile!
        """,
                        inline=False)
        embed.add_field(name="Info Commands",
                        value=f"""
{self.bot.prefix}ping - Gives you bot's latency.
{self.bot.prefix}info - Gives you information regarding the bot.
{self.bot.prefix}status - Gives you the current status of the bot.
{self.bot.prefix}invite - Invite the bot to your server!
        """,
                        inline=False)
        embed.add_field(name="Admin Commands",
                        value=f"""
{self.bot.prefix}say - Makes the bot say something.
{self.bot.prefix}purge - Deletes a certain amount of messages.
{self.bot.prefix}deletechannel - Deletes the specified channel. 
{self.bot.prefix}setsuggestionchannel [ssc] - Sets the channel which suggestions will be posted in.
{self.bot.prefix}setlogchannel [slc] - Sets the channel which commands used will be logged in.
{self.bot.prefix}removelogchannel [rlc] - Removes the channel which commands used will be logged in.
        """,
                        inline=False)
        embed.set_footer(text=f"Use {self.bot.prefix}help <module> for more!")
        await ctx.send(embed=embed)
    elif cmd == "suggest" or cmd == "suggestion":
        await ctx.send(
            f"Use the command `{self.bot.prefix}ssc <#channel>` to set the suggestion channel and `{self.bot.prefix}suggest <suggestion>` to make a suggestion"
        )
    elif cmd == "log" or cmd == "logs":
        await ctx.send(
            f"Use the command `{self.bot.prefix}slc <#channel>` to set the logs channel and `{self.bot.prefix}rlc` remove the log channel"
        )
    elif cmd == "economy":
      embed = discord.Embed(title = "Economy Commands",
                        description = f"""
{self.bot.prefix}start - Build a factory!.
{self.bot.prefix}guide - View a quick guide on the economy when you are lost!
{self.bot.prefix}sell - Sells all the kitkats you have made.
{self.bot.prefix}fish - Go fishing!
{self.bot.prefix}balance - Shows you how much coins you have earned.
{self.bot.prefix}upgrades - Shows you the avaliable upgrades.
{self.bot.prefix}daily - Claim a free gift every day!
{self.bot.prefix}weekly - Claim a free gift every week!
{self.bot.prefix}monthly - Claim a free gift every month!
{self.bot.prefix}leaderboard - View the leaderbord!
{self.bot.prefix}prestige - View the various prestiges
{self.bot.prefix}pets - Buy a lovely pet to acompany you throughout your kitkat making journey!
{self.bot.prefix}coinflip - Do a coinflip! Double your bet or lose it all!
{self.bot.prefix}profile - View someone's profile!
""", color = discord.Color.green())
      await ctx.send(embed = embed)
    elif cmd == "pet" or cmd == "pets":
      embed = discord.Embed(title = "Pet Commands",
                        description = f"""
{self.bot.prefix}pet - View your current pet.
{self.bot.prefix}pet list - View the avaliable pets!
{self.bot.prefix}pet buy <name> - Buy a pet.
{self.bot.prefix}pet name <name> - Give your pet a nice name!
{self.bot.prefix}pet upgrade - Upgrades your pet to the next level. (View upgrade costs using `{self.bot.prefix}pet`)
{self.bot.prefix}hunt - Lets you pet go hunting and get some free coins!
""", color = discord.Color.green())
      await ctx.send(embed = embed)

# Ping
@bot.command()
async def ping(ctx):
    await ctx.send(f"Ping: `{round(bot.latency * 1000)}ms`")


# Quotes
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]["a"]
    return quote


@bot.command()
async def inspire(ctx):
    quote = get_quote()
    await ctx.channel.send(quote)


@bot.command(aliases = ["randint", "randomnum"])
async def randomint(ctx, num1: int = None, num2: int = None):
    if num1 is None or num2 is None:
        await ctx.send(
            f"Please pick 2 integers! (`{self.bot.prefix}randomint <num1> <num2>`)"
        )
    elif num1 == num2:
        await ctx.send(
            f"Please pick 2 different integers! (`{self.bot.prefix}randomint <num1> <num2>`)"
        )
    elif len(str(num1)) >= 2000 or len(str(num2)) >= 2000:
      await ctx.reply(f"Please pick a number shorter than 2000 characters!")
    else:
        if num1 > num2:
            number1 = num2
            number2 = num1
        elif num1 < num2:
            number1 = num1
            number2 = num2

        await ctx.reply(
            f"Your random number: `{random.randint(number1, number2)}`")


@randomint.error
async def randomint_error(ctx, error):
    await ctx.send(
        f"Please pick 2 integers! (`{self.bot.prefix}randomint <num1> <num2>`)"
    )
    await ctx.send(str(error))


#    await ctx.send(str(error))


@bot.command()
async def status(ctx):
    embed = discord.Embed(
        title="KitkatBot's Status",
        description=
        "[Here](https://KitkatBot.kitkat3141.repl.co) is the status of the bot!",
        color=discord.Color.blue())
    embed.set_author(name=ctx.message.author,
                     url=ctx.author.avatar_url,
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command()
async def invite(ctx):
    embed = discord.Embed(
        title="Invite KitkatBot to your server!",
        description=
        "Invite: https://discord.com/api/oauth2/authorize?client_id=919773782451830825&permissions=1617525468241&scope=bot",
        color=discord.Color.green())
    await ctx.reply(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, a=None):

    if a is None:
        await ctx.send("Please use `?say <message>`")
    else:
        await ctx.message.delete()
        await ctx.send(a)


# VERSION FOR KITKAT
@bot.command()
async def says(ctx, *, a=None):
    if ctx.author.id == 915156033192734760:
        if a is None:
            await ctx.send("Please use `?say <message>`")
        else:
            await ctx.message.delete()
            await ctx.send(a)


@say.error
async def nick_error(ctx, error):
    await ctx.send(str(error))


@bot.command(pass_context=True)
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member = None, *, nick=None):
    if None in (member, nick):
        await ctx.send(
            f"Please use `{self.bot.prefix}nick <@user> <new nickname>`")
    else:
        await ctx.message.delete()
        await member.edit(nick=nick)
        await ctx.send(f'Nickname was changed for {member.mention} ')


@nick.error
async def nick_error(ctx, error):
    await ctx.send(str(error))


@bot.command()
async def resetnick(ctx):
    if ctx.message.author.id == 915156033192734760:
        await ctx.message.guild.me.edit(nick="KitkatBot")
        await ctx.send("Bot's nickname successfully reset!")
    else:
        await ctx.send("This can only be used by kitkat3141!")


@resetnick.error
async def resetnick_error(ctx, error):
    await ctx.send(str(error))


@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
@commands.cooldown(1, 4, commands.BucketType.user)
async def purge(ctx, limit: int = None):
    if limit is None:
        await ctx.reply("Please use `?purge <amount>`")
    else:
        if limit <= 100 and limit > 0:
            await asyncio.sleep(0.5)
            await ctx.message.delete()
            await ctx.channel.purge(limit=limit)
            message = await ctx.send(
                f"{ctx.author.mention} just cleared {limit} messages")
            await asyncio.sleep(3)
            await message.delete()
        elif limit > 100:
            message = await ctx.reply("You can only clear up to 100 messages!")
            await asyncio.sleep(3)
            await ctx.message.delete()
            await message.delete()
        else:
            message = await ctx.reply("Please specify a number from 1 to 100!")
            await asyncio.sleep(3)
            await ctx.message.delete()
            await message.delete()


@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.reply(
            "Please specify a number from 1 to 100! Eg. `?purge 10`")
    else:
        await ctx.send(str(error))


# -- Suggestion commands --
@bot.command()
async def suggest(ctx, *, suggestion=None):
    if str(ctx.guild.id
           ) in self.bot.db["suggestion_channels"] and ctx.guild.get_channel(
               self.bot.db["suggestion_channels"][str(ctx.guild.id)]) is not None:
        if suggestion is None:
            await ctx.send("Please use `?suggest <suggestion>`")
        else:
            embed = discord.Embed(
                title="Suggestion Sent!",
                description=
                f"Your suggestion was sent to <#{ctx.guild.get_channel(db['suggestion_channels'][str(ctx.guild.id)]).id}>",
                color=discord.Color.blue())
            embed.set_author(name=ctx.message.author,
                             url=ctx.author.avatar_url,
                             icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

            embed = discord.Embed(title="**Suggestion**",
                                  description=f"**Suggestion:** {suggestion}",
                                  color=discord.Color.blue())
            embed.set_footer(text = f"Suggested by {ctx.author}")
            sent_suggestion = await ctx.guild.get_channel(
                self.bot.db["suggestion_channels"][str(ctx.guild.id)]).send(embed=embed)
            await sent_suggestion.add_reaction("\u2705")
            await sent_suggestion.add_reaction("\u274e")
    else:
        await ctx.reply(
            f"Please set a suggestion channel using `{self.bot.prefix}ssc <#channel>`"
        )


@suggest.error
async def suggest_error(ctx, error):
    if isinstance(error, AttributeError):
        await ctx.send(
            f"Please set a suggestion channel using `{self.bot.prefix}ssc <#channel>`"
        )
        await ctx.send(str(error))

@bot.command()
@commands.has_permissions(administrator=True)
async def suggestion(ctx, msg_id = None, status = None, *, reason = None):
  if reason is not None:
    guild = bot.get_guild(ctx.guild.id)
    channel = guild.get_channel(db["suggestion_channels"][str(ctx.guild.id)])
    msg = await channel.fetch_message(msg_id)
    if status in ("accept", "deny"):
      if status == "accept":
        embed = discord.Embed(
          title = "Suggestion Accepted",
          description = f"{msg.embeds[0].description} \n\nStatus: `{reason}`",
          color = discord.Color.green()
        )
        reply = discord.Embed(
          title = "Suggestion Accepted!", 
          description = f"You have accepted a suggestion. \nReason: **{reason}**",
          color = discord.Color.green()
        )
      elif status == "deny":
        embed = discord.Embed(
          title = "Suggestion Denied",
          description = f"{msg.embeds[0].description} \n\nReason: `{reason}`",
          color = discord.Color.red()
        )
        reply = discord.Embed(
          title = "Suggestion Denied!", 
          description = f"You have denied a suggestion. \nReason: **{reason}**",
          color = discord.Color.red()
        )
      await ctx.reply(embed = reply)
      await msg.edit(embed = embed)
    else: 
      await ctx.reply(f"Please use `{self.bot.prefix}suggestion <message_id> <accept / deny> <reason>`")
  else:
    await ctx.reply(f"Please use `{self.bot.prefix}suggestion <message_id> <accept / deny> <reason>`")

@bot.command(aliases=["ssc"])
@commands.has_permissions(manage_channels=True)
async def setsuggestionchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("Please use `?ssc <#channel>`")
    else:
        self.bot.db["suggestion_channels"][str(ctx.guild.id)] = channel.id
        val = self.bot.db['suggestion_channels'][str(ctx.guild.id)]
        embed = discord.Embed(
            title="Suggestion Channel",
            description=
            f"The suggestion channel has been set to <#{ctx.guild.get_channel(val).id}>",
            color=discord.Color.blue())
        await ctx.send(embed=embed)

@suggestion.error
async def suggestion_error(ctx, error):
  if isinstance(error, MissingPermissions):
    await ctx.send(str(error))
  else:
    await ctx.reply(f"Please use a valid message id! `{self.bot.prefix}suggestion <message_id> <accept / deny> <reason>`")

@setsuggestionchannel.error
async def ssc_error(ctx, error):
    await ctx.send(str(error))


@bot.command(aliases=["sc"])
async def suggestionchannel(ctx):
    embed = discord.Embed(
        title="Suggestion",
        description=
        f"The suggestion channel is currently set to <#{ctx.guild.get_channel(db[str(ctx.guild.id)]).id}>",
        color=discord.Color.blue())
    await ctx.send(embed=embed)


# Bot Info
@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="KitkatBot",
        description="This bot was created by kitkat3141#0422 on 13/12/21 with a lot of help from PythonRocks1234#4380.",
        color=discord.Color.blue())
    embed.add_field(
        name="Get help",
        value=f"Use {self.bot.prefix}help to get the avaliable commands and join the official KitkatBot server [here](https://discord.gg/hhVwjFBJ2C)!",
        inline=True)
    embed.set_footer(text=f"?info called by {ctx.message.author}")

    await ctx.send(embed=embed)
@info.error
async def info_error(ctx, error):
    await ctx.send(str(error))

@bot.command(aliases = ["discord"])
async def serverinvite(ctx):
  embed = discord.Embed(
        title="KitkatBot's Official Discord",
        description="Join the official KitkatBot server [here](https://discord.gg/hhVwjFBJ2C)!",
        color=discord.Color.blue())
  await ctx.reply(embed = embed)

@bot.command()
async def embed(ctx, title = None, *, content = None):
  if ctx.author.id == 915156033192734760:
    if title is not None and content is not None:
      embed = discord.Embed(
        title = title,
        description = content,
        color = discord.Color.green()
      )
      await ctx.send(embed = embed)

# -- TIC TAC TOE --

winningConditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7],
                     [2, 5, 8], [0, 4, 8], [2, 4, 6]]
ttt_var = {}

@bot.command(aliases=["ttt"])
async def tictactoe(ctx, p1: discord.Member):
  global ttt_var
  if str(ctx.guild.id) not in ttt_var or ttt_var[str(ctx.guild.id)]["gameOver"] == True:
    ttt_var[str(ctx.guild.id)]={
        "count": 0,
        "player1": "",
        "player2": "",
        "turn": "",
        "gameOver": True,
        "board": [],
        "mark": "",
        "line": "",
        "new_board": []
    }

    ttt_var[str(ctx.guild.id)]["board"] = [
        ":white_large_square:", ":white_large_square:", ":white_large_square:",
        ":white_large_square:", ":white_large_square:", ":white_large_square:",
        ":white_large_square:", ":white_large_square:", ":white_large_square:"
    ]
    if ttt_var[str(ctx.guild.id)]["gameOver"] == True and p1 != ctx.author:
        if not p1.bot:
            ttt_var[str(ctx.guild.id)]["turn"] = ""
            ttt_var[str(ctx.guild.id)]["gameOver"] = False
            ttt_var[str(ctx.guild.id)]["count"] = 0
            ttt_var[str(ctx.guild.id)]["player1"] = p1
            ttt_var[str(ctx.guild.id)]["player2"] = ctx.author
            


            # determine who goes first
            num = random.randint(1, 2)
            if num == 1:
                ttt_var[str(ctx.guild.id)]["turn"] = ttt_var[str(ctx.guild.id)]["player1"]
                b = str(ttt_var[str(ctx.guild.id)]["player1"].id)
                msg = f"It is <@{b}>'s turn."
            elif num == 2:
                ttt_var[str(ctx.guild.id)]["turn"] = ttt_var[str(
                    ctx.guild.id)]["player2"]
                b = str(ttt_var[str(ctx.guild.id)]["player2"].id)
                msg = f"It is <@{b}>'s turn."
            # print the board
            ttt_var[str(ctx.guild.id)]["line"] = ""
            for x in range(len(ttt_var[str(ctx.guild.id)]["board"])):
                if x in (3, 6, 9):
                    ttt_var[str(
                        ctx.guild.id)]["line"] += "\n" + ttt_var[str(
                            ctx.guild.id)]["board"][x]
                else:
                    ttt_var[str(
                        ctx.guild.id)]["line"] += " " + ttt_var[str(
                            ctx.guild.id)]["board"][x]
            await ctx.send(ttt_var[str(ctx.guild.id)]["line"])
            await ctx.send(
                f"\nPlease do `{self.bot.prefix}place <position>` in 30 seconds or the game will be forfeited! \n{msg}"
            )
            ttt_var[str(ctx.guild.id)]["line"] = ""
            new_board = ttt_var[str(ctx.guild.id)]["board"].copy()
            await asyncio.sleep(30)
            if new_board == ttt_var[str(ctx.guild.id)]["board"]:
                ttt_var[str(ctx.guild.id)]["gameOver"] = True
                b = ttt_var[str(ctx.guild.id)]["turn"]
                await ctx.send(
                    f"The game ended because {b} did not respond!. Use `{self.bot.prefix}tictactoe` to start a new game!"
                )
                
        else:
            await ctx.send(f"Please make sure both players are not bots!")
            #elif p1 == p2:
            await ctx.send("Please choose 2 different players!")
  else:
      await ctx.send(
          "A game is already in progress! Finish it before starting a new one."
        )


ttt_timer = 60


@bot.command()
async def place(ctx, pos: int):
    global ttt_var
    if ttt_var[str(ctx.guild.id)]["gameOver"] == False:
        ttt_var[str(ctx.guild.id)]["mark"] = ""
        if ttt_var[str(ctx.guild.id)]["turn"] == ctx.author:
            if ttt_var[str(ctx.guild.id)]["turn"] == ttt_var[str(
                    ctx.guild.id)]["player1"]:
                ttt_var[str(
                    ctx.guild.id)]["mark"] = ":regional_indicator_x:"
            elif ttt_var[str(ctx.guild.id)]["turn"] == ttt_var[str(ctx.guild.id)]["player2"]:
                ttt_var[str(ctx.guild.id)]["mark"] = ":o2:"
            if 0 < pos < 10 and ttt_var[str(
                    ctx.guild.id)]["board"][pos - 1] == ":white_large_square:":
                ttt_var[str(ctx.guild.id)]["board"][pos - 1] = ttt_var[str(ctx.guild.id)]["mark"]
                ttt_var[str(ctx.guild.id)]["count"] += 1

                # print the board
                ttt_var[str(ctx.guild.id)]["line"] = ""
                for x in range(len(ttt_var[str(ctx.guild.id)]["board"])):
                    if x in (3, 6, 9):
                        ttt_var[str(ctx.guild.id)]["line"] += "\n" + ttt_var[str(
                                ctx.guild.id)]["board"][x]
                    else:
                        ttt_var[str(ctx.guild.id)]["line"] += " " + ttt_var[str(ctx.guild.id)]["board"][x]
                await ctx.send(ttt_var[str(ctx.guild.id)]["line"])
                ttt_var[str(ctx.guild.id)]["line"] = ""

                checkWinner(ctx, winningConditions,
                            ttt_var[str(ctx.guild.id)]["mark"])
                print(ttt_var[str(ctx.guild.id)]["count"])
                if ttt_var[str(ctx.guild.id)]["gameOver"] == True:
                    b = ttt_var[str(ctx.guild.id)]["mark"]
                    await ctx.send(f"{b} wins!")
                elif ttt_var[str(ctx.guild.id)]["count"] >= 9:
                    ttt_var[str(ctx.guild.id)]["gameOver"] = True
                    await ctx.send("It's a tie!")

                # switch turns
                if ttt_var[str(ctx.guild.id)]["turn"] == ttt_var[str(ctx.guild.id)]["player1"] and not ttt_var[str(ctx.guild.id)]["gameOver"]:
                    ttt_var[str(ctx.guild.id)]["turn"] = ttt_var[str(ctx.guild.id)]["player2"]
                    b = str(ttt_var[str(ctx.guild.id)]["player2"].id)
                    await ctx.send(f"It is now <@{b}>'s turn. \nUse `{self.bot.prefix}place <position>` to play!")
                elif ttt_var[str(ctx.guild.id)]["turn"] == ttt_var[str(ctx.guild.id)]["player2"] and not ttt_var[str(ctx.guild.id)]["gameOver"]:
                    ttt_var[str(ctx.guild.id)]["turn"] = ttt_var[str(ctx.guild.id)]["player1"]
                    b = str(ttt_var[str(ctx.guild.id)]["player1"].id)
                    await ctx.send(f"It is now <@{b}>'s turn. \nUse `{self.bot.prefix}place <position>` to play!")
                
                new_board = ttt_var[str(ctx.guild.id)]["board"].copy()

                await asyncio.sleep(45)
                if new_board == ttt_var[str(ctx.guild.id)]["board"] and ttt_var[str(ctx.guild.id)]["gameOver"] == False:
                    ttt_var[str(ctx.guild.id)]["gameOver"] = True
                    b = ttt_var[str(ctx.guild.id)]["turn"]
                    await ctx.send(
                        f"{b} did not place in time. Use `{self.bot.prefix}tictactoe` to start a new game!"
                    )
            else:
                await ctx.send(
                    f"Be sure to choose an unoccupied position from 1 to 9. (`{self.bot.prefix}place <position>`)"
                )
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send(
            f"Please start a new game using `{self.bot.prefix}tictactoe` command."
        )


def checkWinner(ctx, winningConditions, mark):
    global ttt_var
    for condition in winningConditions:
        if ttt_var[str(ctx.guild.id)]["board"][condition[0]] == ttt_var[str(ctx.guild.id)]["mark"] and ttt_var[str(ctx.guild.id)]["board"][condition[1]] == ttt_var[str(ctx.guild.id)]["mark"] and ttt_var[str(ctx.guild.id)]["board"][condition[2]] == ttt_var[str(ctx.guild.id)]["mark"]:
            ttt_var[str(ctx.guild.id)]["gameOver"] = True

@tictactoe.error
async def ttt_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please use `?tictactoe <@user>`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please use `?tictactoe <@user>`.")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")
    else:
        await ctx.send(str(error))



# -- GIVEAWAY COMMAND --
@bot.command(aliases=["sgc"])
@commands.has_permissions(manage_channels=True)
async def setgiveawaychannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("Please use `?sgc <#channel>`")
    else:
        self.bot.db["giveaway_channels"][str(ctx.guild.id)] = channel.id
        val = self.bot.db['giveaway_channels'][str(ctx.guild.id)]
        embed = discord.Embed(
            title="Giveaway Channel",
            description=
            f"The giveaway channel has been set to <#{ctx.guild.get_channel(val).id}>",
            color=discord.Color.green())
        await ctx.send(embed=embed)


@setgiveawaychannel.error
async def sgc_error(ctx, error):
    await ctx.send(str(error))


@bot.command(aliases = ["giveaway", "giveaways"])
async def gcreate(ctx, time=None, *, prize=None):
    if str(ctx.guild.id) in self.bot.db["giveaway_channels"] and ctx.guild.get_channel(
            self.bot.db["giveaway_channels"][str(ctx.guild.id)]) is not None:
        if time is None:
            return await ctx.send(
                f"Please enter a time and a prize! `({self.bot.prefix}gcreate <time> <prize> | s = seconds, m = minutes, h = hours, d = days`)"
            )
        elif prize is None:
            await ctx.send(
                f"Please enter a prize! (`{self.bot.prefix}gcreate <time> <prize>`)"
            )

        time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        gw_time = int(time[:-1]) * time_convert[time[-1]]

        embed = discord.Embed(
            title="Giveaway Posted!",
            description=
            f"Your giveaway was posted in <#{ctx.guild.get_channel(db['giveaway_channels'][str(ctx.guild.id)]).id}>",
            color=discord.Color.blue())
        embed.set_author(name=ctx.message.author,
                         url=ctx.author.avatar_url,
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        embed = discord.Embed(
            title=f"{prize}",
            description=
            f"React with :tada: to enter the giveaway! \nEnds: <t:{int(_time.time()) + gw_time}:R> | <t:{int(_time.time()) + gw_time}> \nHosted by: {ctx.author.mention}",
            color=discord.Color.green())
        gw_msg = await ctx.guild.get_channel(db["giveaway_channels"][str(
            ctx.guild.id)]).send(embed=embed)
        await gw_msg.add_reaction("🎉")

        await asyncio.sleep(gw_time)

        channel_posted = ctx.guild.get_channel(db["giveaway_channels"][str(
            ctx.guild.id)])
        new_gw_msg = await channel_posted.fetch_message(gw_msg.id)
        user_list = [
            u for u in await new_gw_msg.reactions[0].users().flatten()
            if u != bot.user
        ]

        if len(user_list) == 0:
            await gw_msg.reply("No one reacted.")
        else:
            winner = random.choice(user_list)
            await gw_msg.reply(f"{winner.mention} has won **{prize}**!")
    else:
        await ctx.reply(
            f"Please set the giveaway channel by using `{self.bot.prefix}sgc <#channel>`"
        )


@gcreate.error
async def gcreate_error(ctx, error):

    if isinstance(error, (KeyError, AttributeError)):
        await ctx.send(
            f"Please set the giveaways channel using `?sgc <#channel>`")
    else:

        await ctx.send(
            f"Please specify the duration. (`{self.bot.prefix}gcreate <time> <prize> | s = seconds, m = minutes, h = hours, d = days`)"
        )

        await ctx.send(str(error))




@bot.command()
@commands.has_permissions(manage_channels=True)
async def deletechannel(ctx, *, channel: discord.TextChannel = None):
    # if the channel exists
    if channel is not None:
        embed = discord.Embed(
            title=f"Channel Deletion",
            description=
            f"React with a ✅ to confirm the deletion of **{channel.mention}**",
            color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
            
            # This makes sure nobody except the command sender can interact with the "menu"

        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=60,
                                                check=check)
            # waiting for a reaction to be added - times out after x seconds, 60
            if str(reaction.emoji) == "✅":
                await channel.delete()
                new_embed = discord.Embed(
                    title=f"Channel Deletion",
                    description=f"**#{channel}** has been deleted.",
                    color=discord.Color.green())
                await msg.edit(embed=new_embed)

        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time.")

    # if the channel does not exist, inform the user
    else:
        await ctx.send(f'No channel named, "{channel}", was found')


@deletechannel.error
async def deletechannel_error(ctx, error):
    await ctx.send(str(error))


@bot.command()
@commands.has_permissions(manage_channels=True)
async def createchannel(ctx, *, channel=None):
    # if the channel exists
    if channel is not None:
        embed = discord.Embed(
            title=f"Channel Creation",
            description=
            f"React with a ✅ to confirm the creation of **#{channel}**",
            color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
            # This makes sure nobody except the command sender can interact with the "menu"

        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=60,
                                                check=check)
            # waiting for a reaction to be added - times out after x seconds, 60
            if str(reaction.emoji) == "✅":
                new_channel = await ctx.guild.create_text_channel(str(channel))
                new_embed = discord.Embed(
                    title=f"Channel Creation",
                    description=f"**{new_channel.mention}** has been created.",
                    color=discord.Color.green())
                await msg.edit(embed=new_embed)

        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time.")

    else:
        await ctx.send(f"Please use `{self.bot.prefix}createchannel <name>`"
                       )


@createchannel.error
async def createchannel_error(ctx, error):
    await ctx.send(str(error))


# -- ECONOMY --
coin = ":coin:"
choco = "🍫"
eco_prestige = [0, 1000000, 2500000, 5000000, 10000000, 20000000]
@bot.command()
async def start(ctx):
  if str(ctx.author.id) not in self.bot.db["economy"]:
    self.bot.db["economy"][str(ctx.author.id)] = {"balance" : 10 , "last_sold" : int(_time.time()), "workers" : 1, "machine_level" : 1, "storage" : 200, "last_daily" : 1, "last_weekly" : 1, "last_monthly" : 1, "prestige" : 0, "kitkats_sold" : 0, "last_cf": 1, "upgrade_cap" : 10, "sponsor" : 0, "chests" : 0, "fish" : {"last_fish" : 0, "rod_level" : 1}, "pets" : {"name": "", "type": "", "tier" : 0, "level": 0, "last_hunt" : 1}, "daily_streak" : 0}
    embed = discord.Embed(
      title = "**Kitkat Factory**", 
      description = f"""Hello {ctx.author.mention}, you have successfully built a factory! Welcome to your very own **Kitkat Factory!** 
Currently, you are producing kitkats at a rate of `3 {choco} / minute`! To sell the kitkats, all you need to do is `{self.bot.prefix}sell`! 
Making upgrades to your factory will increase your kitkats' value!
Current kitkat value: **2 {coin} / kitkat**.
    
To produce kitkats at a faster rate, you can either hire more workers or upgrade your machine! You can do `{self.bot.prefix}upgrades` for more information on that! To view your balance, you can do `{self.bot.prefix}balance`.
You can also get your own pet by doing `{self.bot.prefix}pet`! Having a pet gives you access to the `{self.bot.prefix}hunt` command, which gives you a random amount of coins every hour!

Lastly, `{self.bot.prefix}guide` will always be avaliable to those who are confused on how the factory works! You can also view the leaderboard using `{self.bot.prefix}leaderboard` and prestige using `{self.bot.prefix}prestige`. 

To join giveaways, lotteries and more, you can join KitkatBot's official server by clicking [here](https://discord.gg/hhVwjFBJ2C)! Here's a free **10{coin}** to get you started on your journey. Remember to do `{self.bot.prefix}daily` everyday to claim a free gift, good luck!""", 
color = discord.Color.green()
    )
    await ctx.reply(embed = embed)
  else:
    await ctx.reply(f"You already own a factory! Do `{self.bot.prefix}help economy` to see the commands you can use!")
@start.error
async def start_error(ctx, error):
  await ctx.send(str(error))


@bot.command()
async def guide(ctx):
  if str(ctx.author.id) in self.bot.db["economy"]:
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]

    rate_of_kitkats = (workers + 2) * machine_lvl
    embed = discord.Embed(
      title = "**The kitkat factory guide!**", 
      description = f"""Hello {ctx.author.mention}, it looks like you are lost! Do not worry, `?guide` will always be avaliable to you! 

Currently, you are producing kitkats at a rate of `{rate_of_kitkats} {choco} / minute`! To sell the kitkats, all you need to do is `{self.bot.prefix}sell`! 
Making upgrades to your factory will increase your kitkats' value!
Current kitkat value: **2 {coin} / kitkat**.
      
To produce kitkats at a faster rate, you can either hire more workers or upgrade your machine! You can do `{self.bot.prefix}upgrades` for more information on that! To view your balance, you can do `{self.bot.prefix}balance`.
You can also get your own pet by doing `{self.bot.prefix}pet`! Having a pet gives you access to the `{self.bot.prefix}hunt` command, which gives you a random amount of coins every hour!

You can view the leaderboard using `{self.bot.prefix}leaderboard` and prestige using `{self.bot.prefix}prestige`. To join giveaways, lotteries and more, you can join KitkatBot's official server by clicking [here](https://discord.gg/hhVwjFBJ2C)! Remember to do `{self.bot.prefix}daily` everyday to claim a free gift, good luck!""", 
color = discord.Color.green()
    )
    await ctx.reply(embed = embed)
  elif str(ctx.author.id) not in self.bot.db["economy"]:
    await ctx.reply(f"Looks like you do not own a factory! Do `{self.bot.prefix}start` to build one!")

@bot.command(aliases = ["s"])
async def sell(ctx):
  if str(ctx.author.id) in self.bot.db["economy"]:
    last_sold = self.bot.db["economy"][str(ctx.author.id)]["last_sold"]
    time_diff = int(_time.time()) - last_sold
    
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
        self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(_time.time())
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
          self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(_time.time())
          self.bot.db["economy"][str(ctx.author.id)]["balance"] += (math.floor(amt_sold_final * 2/100*5))
          self.bot.db["economy"][str(ctx.author.id)]["kitkats_sold"] += math.floor(amt_sold_final/100*5)
          msg = f"You have sold {amt_sold_final}{choco} and have earned **{amt_sold_final * 2} {coin}** and an extra **{(math.floor(amt_sold_final * 2/100*5))}{coin}** as a prestige bonus! (`+5%`)." 
        elif self.bot.db["economy"][str(ctx.author.id)]["prestige"] < 4:
          amt_sold_final = amt_sold
          self.bot.db["economy"][str(ctx.author.id)]["balance"] += math.floor(amt_sold_final * 2)
          self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(_time.time())
          self.bot.db["economy"][str(ctx.author.id)]["kitkats_sold"] += math.floor(amt_sold_final)
          msg = f"You have sold {amt_sold_final}{choco} and have earned **{math.floor(amt_sold_final * 2)} {coin}**! "
      
      msg += f"You are currently producing `{str(rate_of_kitkats)}{choco} / minute`"
      await ctx.reply(msg)
  else: 
    await ctx.reply(f"You do not own a factory yet! To create one, you can do `{self.bot.prefix}start`!")
@sell.error
async def sell(ctx, error):
  await ctx.send(str(error))

@bot.command(aliases = ["b", "bal"])
async def balance(ctx, user: discord.Member = None):
  if user is None:
    if str(ctx.author.id) in self.bot.db["economy"]:
      balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
      bal = "{:,}".format(balance)
      await ctx.reply(f"Your balance is **{bal}{coin}**! You can do `{self.bot.prefix}sell` to sell your current kitkats and earn more money!")
    else:
      await ctx.reply(f"You do not own a factory! To create one, you can use the command `{self.bot.prefix}start`!")
  else:
    if str(user.id) in self.bot.db["economy"]:
      balance = self.bot.db["economy"][str(user.id)]["balance"]
      bal = "{:,}".format(balance)
      await ctx.reply(f"{user}'s balance is **{bal}{coin}!**")
    else:
      await ctx.reply(f"{user} does not own a factory! Create one using the command `{self.bot.prefix}start`!")
@balance.error
async def bal_error(ctx, error):
  await ctx.send(str(error))

@bot.command(aliases = ["d"])
async def daily(ctx):
#  if ctx.author.id == 915156033192734760:
  if str(ctx.author.id) in self.bot.db["economy"]:
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    last_daily = self.bot.db["economy"][str(ctx.author.id)]["last_daily"]
    current_time = int(_time.time())
    rate_of_kitkats = (workers + 2) * machine_lvl
    daily_coins = int(rate_of_kitkats) * 100
    daily_streak = self.bot.db["economy"][str(ctx.author.id)]["daily_streak"]
    
    if current_time >= (last_daily + 86400):
      pres_coins = 0
      streak_bonus = 500
      if current_time >= (last_daily + 86400*2):
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

      self.bot.db["economy"][str(ctx.author.id)]["last_daily"] = _time.time()
      self.bot.db["economy"][str(ctx.author.id)]["balance"] += total_coins
      updated_bal = balance + total_coins
      if self.bot.db["economy"][str(ctx.author.id)]["prestige"] < 2:
        msg = f"Daily reward: **{daily_coins}{coin}** \nStreak Bonus: **{streak_coins}{coin}** \nTotal Reward: **{total_coins}{coin}** \n\nCurrent Balance: **{updated_bal}{coin}** \nDaily Streak: `{daily_streak}` "
      else: 
        msg = f"Daily reward: **{daily_coins}{coin}** \nPrestige bonus: **{pres_coins}{coin}** (+{rate}) \nStreak Bonus: **{streak_coins}{coin}** \nTotal Reward: **{total_coins}{coin}** \n\nCurrent Balance: **{updated_bal}{coin}** \nDaily Streak: `{daily_streak}` "
      
      embed = discord.Embed(
        title = "Daily Reward",
        description = msg,
        color = discord.Color.green()
      )
      await ctx.reply(embed = embed)
    else:
      td = timedelta(seconds=86400-current_time+last_daily)
      hours_left = td.seconds // 3600
      mins_left = (td.seconds % 3600) // 60
      secs_left = td.seconds % 60
      embed = discord.Embed(
        title = "Daily Reward",
        description = f"You can claim your daily gift in `{hours_left}h {mins_left}m {secs_left}s`. \nDaily Streak: `{daily_streak}`", 
        color = discord.Color.red()
      )
      await ctx.reply(embed = embed)
  else: 
    await ctx.reply(f"Whoops, looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!")
#    await ctx.reply("This command has been temporarily disabled.")
@bot.command(aliases = ["w"])
async def weekly(ctx):
  if str(ctx.author.id) in self.bot.db["economy"]:
    if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 1:
      workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
      machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
      balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
      last_weekly = self.bot.db["economy"][str(ctx.author.id)]["last_weekly"]
      current_time = int(_time.time())
      rate_of_kitkats = (workers + 2) * machine_lvl
      weekly_coins = (int(rate_of_kitkats) + 20) * 800

      if current_time >= (last_weekly + 604800):
        self.bot.db["economy"][str(ctx.author.id)]["last_weekly"] = int(_time.time())
        self.bot.db["economy"][str(ctx.author.id)]["balance"] += weekly_coins
        await ctx.reply(f"You have claimed your weekly gift of **{weekly_coins}{coin}!** \nCurrent balance: **{balance + weekly_coins}{coin}**")
      else:
        td = timedelta(seconds=604800-current_time+last_weekly)
        days_left = td.days
        hours_left = td.seconds // 3600
        mins_left = (td.seconds % 3600) // 60
        secs_left = td.seconds % 60
        await ctx.reply(f"You can claim your weekly gift in `{days_left}d {hours_left}h {mins_left}m {secs_left}s`. ")
    else:
      await ctx.reply(f"This is a prestige 1 feature! Do `{self.bot.prefix}prestige` to view prestige costs!")
  else: 
    await ctx.reply(f"Whoops, looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!")

@bot.command(aliases = ["m"])
async def monthly(ctx):
  if str(ctx.author.id) in self.bot.db["economy"]:
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    last_monthly = self.bot.db["economy"][str(ctx.author.id)]["last_monthly"]
    current_time = int(_time.time())
    rate_of_kitkats = (workers + 2) * machine_lvl
    monthly_coins = (int(rate_of_kitkats) + 20) * 2000

    if current_time >= (last_monthly + 2592000):
      self.bot.db["economy"][str(ctx.author.id)]["last_monthly"] = _time.time()
      self.bot.db["economy"][str(ctx.author.id)]["balance"] += monthly_coins
      await ctx.reply(f"You have claimed your monthly gift of **{monthly_coins}{coin}!** \nCurrent balance: **{balance + monthly_coins}{coin}**")
    else:
      td = timedelta(seconds=2592000-current_time+last_monthly)
      days_left = td.days
      hours_left = td.seconds // 3600
      mins_left = (td.seconds % 3600) // 60
      secs_left = td.seconds % 60
      await ctx.reply(f"You can claim your monthly gift in `{days_left}d {hours_left}h {mins_left}m {secs_left}s`. ")
  else: 
    await ctx.reply(f"Whoops, looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!")

@bot.command(aliases = ["cf"])
async def coinflip(ctx, bet = None, amt:int = None):
  if str(ctx.author.id) in self.bot.db["economy"]:
    max_bet = math.floor(db["economy"][str(ctx.author.id)]["balance"] / 2)
    if bet is None:
      await ctx.reply(f"Please choose either heads or tails! `{self.bot.prefix}coinflip <heads/tails> <amount>.`")
    elif amt is None:
      await ctx.reply(f"How much do you want to bet? `{self.bot.prefix}coinflip <heads/tails> <amount>.`")
    elif amt > max_bet:
      await ctx.reply(f"You cannot bet that much! You can only bet half your current balance!")
    elif amt > 200000:
      await ctx.reply(f"You can only bet a maximum of **200,000{coin}!**")
    elif amt < 0:
      await ctx.reply(f"Why are you betting a negative value? Please bet a positive value! `{self.bot.prefix}coinflip <heads/tails> <amount>.`")
    elif amt == 0:
      await ctx.reply(f"Nice try but KitkatBot cannot be fooled! Please make sure your bet is more than 0{coin}! `{self.bot.prefix}coinflip <heads/tails> <amount>.`")
    else:
      last_cf = self.bot.db["economy"][str(ctx.author.id)]["last_cf"]
      current_time = int(_time.time())
      mins_left = str(math.floor((10 - ((current_time - last_cf) % 3600) / 60)))
      secs_left = str(math.floor((60 - ((current_time - last_cf) % 3600) % 60)))
      if int(_time.time()) >= last_cf + 600:
        if bet in ("h", "head", "heads", "t", "tail", "tails"):
          if bet in ("h", "head", "heads"):
            cf_bet = "heads"
          elif bet in ("t", "tail", "tails"):
            cf_bet = "tails"
          result = random.randint(1, 2)
          if result == 1:
            win = "heads"
          elif result == 2:
            win = "tails"
          if win == cf_bet:
            self.bot.db["economy"][str(ctx.author.id)]["balance"] += amt
            await ctx.reply(f"The coin landed on **{win}**! You have earned **{amt}{coin}**")
          elif win != cf_bet:
            self.bot.db["economy"][str(ctx.author.id)]["balance"] -= amt
            await ctx.reply(f"The coin landed on **{win}**. You have lost **{amt}{coin}**")
          self.bot.db["economy"][str(ctx.author.id)]["last_cf"] = int(_time.time())
        else:
          await ctx.reply(f"Please choose either heads or tails! `{self.bot.prefix}coinflip <heads/tails> <amount>`.")  
      else: 
        await ctx.reply(f"Doing too many coinflips will make your fingers tired! Try again in `{mins_left}m {secs_left}s`")
  else:
    await ctx.reply(f"Whoops, looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!")
@coinflip.error
async def cf_error(ctx, error):
  if isinstance(error, commands.BadArgument):
      await ctx.reply(
          f"Make sure your bet is a number! `{self.bot.prefix}coinflip <heads/tails> <amount>`.")
  else:
      await ctx.send(str(error))

@bot.command(aliases = ["stat", "stats"])
async def profile(ctx, user: discord.Member = None):
  if user is None:
    if str(ctx.author.id) in self.bot.db["economy"]:
      embed = discord.Embed(
        title = f"{ctx.author.name}'s profile:",
        description = f"Getting {ctx.author.name}'s statistics...", 
        color = discord.Color.blue()
      )
      embed.set_footer(text = f"Do {self.bot.prefix}profile <@user> to check someone's profile!")

      profile = await ctx.reply(embed = embed)
      workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
      machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
      upgrade_cap = self.bot.db["economy"][str(ctx.author.id)]["upgrade_cap"]
      storage = self.bot.db["economy"][str(ctx.author.id)]["storage"]
      rate_of_kitkats = (workers + 2) * machine_lvl
      balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
      kitkats_sold = self.bot.db["economy"][str(ctx.author.id)]["kitkats_sold"]
      prestige = self.bot.db["economy"][str(ctx.author.id)]["prestige"]
      rod_level = self.bot.db["economy"][str(ctx.author.id)]["fish"]["rod_level"]
      daily_streak = self.bot.db["economy"][str(ctx.author.id)]["daily_streak"]
      msg = f"""Balance: **{balance}{coin}** | `{rate_of_kitkats}{choco} / minute`

Machine Level: `{machine_lvl}`
Workers: `{workers}`
Upgrade Capacity: `{upgrade_cap}`
Kitkat Storage: `{storage}`
Fishing Rod Level: `{rod_level}`
Daily Streak: `{daily_streak}`
Total Kitkats Sold: `{kitkats_sold}{choco}`"""   
      if prestige > 0:
        msg += f"\nPrestige: `{prestige}`"
      else:
        msg += f"\nYou have not prestiged yet! Use `{self.bot.prefix}prestige` to prestige!"

      if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 0:
        msg += f"**\n\nPet Statistics: **{ctx.author.name} does not own a pet! \nDo `{self.bot.prefix}pet list` to view available pets!"

      elif self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] > 0:
        pet_name = self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"]
        pet_tier = self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"]
        pet_type = self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"]
        pet_level = self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"]
        last_hunt = int(db["economy"][str(ctx.author.id)]["pets"]["last_hunt"])
        if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 1:
          cooldown = 3600
          mins_ = 60
        if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 2:
          cooldown = 2700
          mins_ = 45
        if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 3:
          cooldown = 1800
          mins_ = 30
        msg += f"""\n\n**Pet Statistics:**
Name: `{pet_name}`
Type: `{pet_type}`
Tier: `{pet_tier}`
Level: `{pet_level}`
"""   
        if int(_time.time()) < last_hunt + cooldown:
          current_time = int(_time.time())
          last_hunt = self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"]
          mins_left = str(math.floor((mins_ - ((current_time - last_hunt) % 3600) / 60)))
          secs_left = str(math.floor((60 - ((current_time - last_hunt) % 3600) % 60)))
          msg += f"\n`{pet_name}` can hunt again in `{mins_left}m {secs_left}s`"
        else: 
          msg += f"\n`{pet_name}` can go hunting! Do `{self.bot.prefix}hunt` to hunt!"
      new_embed = discord.Embed(
        title = f"{ctx.author.name}'s profile:",
        description = msg, color = discord.Color.green())
      new_embed.set_footer(text = f"Do {self.bot.prefix}profile <@user> to check someone's profile!")
      await profile.edit(embed = new_embed)
    else:
      await ctx.reply(f"Whoops, looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!")
      
    
  else: 
    if str(user.id) in self.bot.db["economy"]:
      embed = discord.Embed(
        title = f"{user.name}'s profile:",
        description = f"Getting {user.name}'s statistics...", 
        color = discord.Color.blue()
      )

      profile = await ctx.reply(embed = embed)
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
      msg = f"""Balance: **{balance}{coin}** | `{rate_of_kitkats}{choco} / minute`

Machine level: `{machine_lvl}`
Workers: `{workers}`
Upgrade Capacity: `{upgrade_cap}`
Kitkat Storage: `{storage}`
Fishing Rod Level: `{rod_level}`
Daily Streak: `{daily_streak}`
Total Kitkats Sold: `{kitkats_sold}{choco}`"""
      if prestige > 0:
        msg += f"\nPrestige: `{prestige}`"
      else:
        msg += f"\n\n**{user}** has not prestiged yet! Use `{self.bot.prefix}prestige` to prestige!"
      if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 0:
        msg += f"\n\n**{user.name}** does not own a pet! \nDo `{self.bot.prefix}pet list` to view available pets!"
      elif self.bot.db["economy"][str(user.id)]["pets"]["tier"] > 0:
        pet_name = self.bot.db["economy"][str(user.id)]["pets"]["name"]
        pet_tier = self.bot.db["economy"][str(user.id)]["pets"]["tier"]
        pet_type = self.bot.db["economy"][str(user.id)]["pets"]["type"]
        pet_level = self.bot.db["economy"][str(user.id)]["pets"]["level"]
        if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 1:
          cooldown = 3600
          mins_ = 60
        if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 2:
          cooldown = 2700
          mins_ = 45
        if self.bot.db["economy"][str(user.id)]["pets"]["tier"] == 3:
          cooldown = 1800
          mins_ = 30
        last_hunt = int(db["economy"][str(user.id)]["pets"]["last_hunt"])
        msg += f"""\n\n**Pet Statistics:**
Name: `{pet_name}`
Type: `{pet_type}`
Tier: `{pet_tier}`
Level: `{pet_level}`
  """
        if int(_time.time()) < last_hunt + cooldown:
          current_time = int(_time.time())
          last_hunt = self.bot.db["economy"][str(user.id)]["pets"]["last_hunt"]
          mins_left = str(math.floor((mins_ - ((current_time - last_hunt) % 3600) / 60)))
          secs_left = str(math.floor((60 - ((current_time - last_hunt) % 3600) % 60)))
          msg += f"\n`{pet_name}` can hunt again in `{mins_left}m {secs_left}s`"
        else: 
          msg += f"\n`{pet_name}` can go hunting! Do `{self.bot.prefix}hunt` to hunt!"
      new_embed = discord.Embed(
        title = f"{user.name}'s profile:",
        description = msg, color = discord.Color.green())
      await profile.edit(embed = new_embed)
    else:
      await ctx.reply(f"That user does not own a factory! Do `{self.bot.prefix}start` to build one!")
@profile.error
async def profile_error(ctx, error):
  await ctx.reply(str(error))

@bot.command(aliases = ["upgrade", "up", "shop"])
async def upgrades(ctx, *, name = None):
  if str(ctx.author.id) in self.bot.db["economy"]:
    workers = self.bot.db["economy"][str(ctx.author.id)]["workers"]
    machine_lvl = self.bot.db["economy"][str(ctx.author.id)]["machine_level"]
    storage = self.bot.db["economy"][str(ctx.author.id)]["storage"]
    total_upgrades = workers + machine_lvl
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    upgrade_cap = self.bot.db["economy"][str(ctx.author.id)]["upgrade_cap"]

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
      embed = discord.Embed(
        title = "Upgrades avaliable:", 
        description = f"""Machine Upgrade: **{machine_upgrade}{coin}**
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
""", 
        color = discord.Color.green()
      )

      await ctx.reply(embed = embed)
    elif name in ("w", "worker", "workers"):
      if balance >= workers_upgrade:
        if upgrade_cap > total_upgrades:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] -= workers_upgrade
          self.bot.db["economy"][str(ctx.author.id)]["workers"] += 1
          embed = discord.Embed(title = "Upgrade Successful!", description = f"You spent {workers_upgrade}{coin} to hire another worker! \n`Total workers: {workers + 1}`", color = discord.Color.green())
          await ctx.reply(embed = embed)
        else:
          await ctx.reply(f"Your upgrade capacity is full! Do `{self.bot.prefix}upgrade capacity` to increase it.")
      else: 
        await ctx.send(f"You do not have enough coins to hire another worker! You need **{workers_upgrade - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!")

    elif name in ("s", "storage", "storages"):
      if balance >= storage_upgrade:
        self.bot.db["economy"][str(ctx.author.id)]["balance"] -= storage_upgrade
        self.bot.db["economy"][str(ctx.author.id)]["storage"] += storage * 2
        embed = discord.Embed(title = "Upgrade Successful!", description = f"Upgrade successfull! You spent {storage_upgrade}{coin} to upgrade your storage capacity! \n`Storage capacity: {storage * 2}`", color = discord.Color.green())
        await ctx.reply(embed = embed)
      else: 
        await ctx.send(f"You do not have enough coins to upgrade your storage! You need **{storage_upgrade - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!")

    elif name in ("m", "machine", "machines"):
      if balance >= machine_upgrade:
        if upgrade_cap > total_upgrades:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] -= machine_upgrade
          self.bot.db["economy"][str(ctx.author.id)]["machine_level"] += 1
          embed = discord.Embed(title = "Upgrade Successful!", description = f"Upgrade successfull! You spent {machine_upgrade}{coin} to upgrade your machine! \nMachine level: `{machine_lvl + 1}`", color = discord.Color.green())
          await ctx.reply(embed = embed)
        else:
          await ctx.reply(f"Your upgrade capacity is full! Do `{self.bot.prefix}upgrade capacity` to increase it.")
      else: 
        await ctx.send(f"You do not have enough coins to upgrade your machine! You need **{machine_upgrade - balance}{coin} more!** Do `{self.bot.prefix}help economy` to explore other commands!")
    elif name == "cap" or name == "capacity":
      if balance >= cap_upgrade:
        self.bot.db["economy"][str(ctx.author.id)]["balance"] -= cap_upgrade
        self.bot.db["economy"][str(ctx.author.id)]["upgrade_cap"] += 10
        embed = discord.Embed(title = "Upgrade Successful!", description = f"Upgrade successfull! You spent {cap_upgrade}{coin} to upgrade your upgrades capacity! \nCurrent Capacity: `{upgrade_cap + 10}`", color = discord.Color.green())
        await ctx.reply(embed = embed)
      else: 
        await ctx.send(f"You do not have enough coins to upgrade your capacity! You need **{cap_upgrade - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!")
    elif name in ("rod", "fish", "fishing rod"):
      if rod_level < 3:
        if balance >= rod_upgrade_:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] -= rod_upgrade_
          self.bot.db["economy"][str(ctx.author.id)]["fish"]["rod_level"] += 1
          embed = discord.Embed(title = "Upgrade Successful!", description = f"Upgrade successfull! You spent {rod_upgrade_}{coin} to upgrade your fishing rod! \nFishing rod level: `{rod_level + 1}`", color = discord.Color.green())
          await ctx.reply(embed = embed)
        else: 
          await ctx.send(f"You do not have enough coins to upgrade your fishing rod! You need **{rod_upgrade_ - balance}{coin}** more! Do `{self.bot.prefix}help economy` to explore other commands!")
      else: 
        await ctx.reply("Your fishing rod is already maxed out!")
  else: 
    await ctx.reply(f"Whoops, it looks like you do not own a factory! You can build one by doing `{self.bot.prefix}start`!")

@bot.command()
async def totalkitkats(ctx):
  total = 0
  for user in self.bot.db["economy"]:
    total += self.bot.db["economy"][user]["kitkats_sold"]
  kitkats = "{:,}".format(total)
  await ctx.reply(f"A total of **{kitkats}{choco}** has been made!")

@bot.command(aliases = ["lb"])
async def leaderboard(ctx, lb = None):
  ecoLB = {}
  if lb is None:
    embed = discord.Embed(
      title = "Kitkat Leaderboard", 
      description = "Getting leaderboard...",
      color = discord.Color.blue()
    )
    old = await ctx.reply(embed = embed)
    for i in self.bot.db["economy"]:
      ecoLB[i] = self.bot.db["economy"][i]["kitkats_sold"]
    if ecoLB != {}:
      top_bal = max(ecoLB.values())
      top_user = list(ecoLB.keys())[list(ecoLB.values()).index(max(ecoLB.values()))]
      guild = bot.get_guild(923013388966166528)
      user = guild.get_member(int(top_user))
      '''
      role = guild.get_role(923435838640103454)
      if ctx.guild.id == 923013388966166528 and len(role.members) > 1:
        for member in role.members:
          await member.remove_roles(role)
      if ctx.guild.id == 923013388966166528 and ctx.guild.get_role(923435838640103454) not in guild.get_member(int(top_user)).roles:
        newer_embed = discord.Embed(
        title = "Kitkat Leaderboard", 
        description = "Adding <@&923435838640103454> to top player...",
        color = discord.Color.red())
        await old.edit(embed = newer_embed)

        
        for member in role.members:
          await member.remove_roles(role)
        await user.add_roles(role)
        '''
    else:
      top_user = "No one here, "
      top_bal = f"do `{self.bot.prefix}help economy` to see avaliable commands!"
    prestige_icons = ["0", "I", "II", "III", "IV", "V"]
    count = 1
    msg = ""
    while count <= 10:
      if ecoLB != {}:
        pres_icon = prestige_icons[db["economy"][top_user]["prestige"]]
        if self.bot.db["economy"][top_user]["prestige"] >= 1:
          if self.bot.db["economy"][top_user]["prestige"] >= 5:
            if top_user != "726965815265722390":
              msg += f"{count}. **:fire:[{pres_icon}] {bot.get_user(int(top_user))}**: **{top_bal}{choco}** \n"
            else:
              msg += f"{count}. **<:trolllol:944407059443617792>:fire:[{pres_icon}] {bot.get_user(int(top_user))}**: **{top_bal}{choco}** \n"
          elif self.bot.db["economy"][top_user]["prestige"] < 5:
            msg += f"{count}. **[{pres_icon}] {bot.get_user(int(top_user))}**: **{top_bal}{choco}** \n"
        else: 
          msg += f"{count}. [{pres_icon}] {bot.get_user(int(top_user))}: **{top_bal}{choco}** \n"
        ecoLB.pop(str(top_user))
        if ecoLB != {}:
          top_bal = max(ecoLB.values())
          top_user = list(ecoLB.keys())[list(ecoLB.values()).index(max(ecoLB.values()))]
        elif ecoLB == {}:
          top_user = "No one here, "
          top_bal = f"do `{self.bot.prefix}help economy` to see avaliable commands!"
        count += 1
      else:
        msg += f"{count}. {top_user} {top_bal} \n"
        count +=1
    members = 0
    for a in self.bot.db["economy"]:
      members += 1
    new_embed = discord.Embed(
      title = "Kitkat Leaderboard", 
      description = msg + f"There are currently `{members}` users producing kitkats!", 
      color = discord.Color.green()
    )
    new_embed.set_footer(text = f"Use {self.bot.prefix}lb coins for coins leaderboard")
    await old.edit(embed = new_embed)


  elif lb == "money" or lb == "coin" or lb == "coins" or lb == "c":
    embed = discord.Embed(
      title = "Coins Leaderboard", 
      description = "Getting leaderboard...",
      color = discord.Color.blue()
    )
    old = await ctx.reply(embed = embed)
    for i in self.bot.db["economy"]:
      ecoLB[i] = self.bot.db["economy"][i]["balance"]
    if ecoLB != {}:
      top_bal = max(ecoLB.values())
      top_user = list(ecoLB.keys())[list(ecoLB.values()).index(max(ecoLB.values()))]
    else:
      top_user = "No one here, "
      top_bal = f"do `{self.bot.prefix}help economy` to see avaliable commands!"
    prestige_icons = ["0", "I", "II", "III", "IV", "V"]
    count = 1
    msg = ""
    while count <= 10:
      if ecoLB != {}:
        pres_icon = prestige_icons[db["economy"][top_user]["prestige"]]
        if self.bot.db["economy"][top_user]["prestige"] >= 1:
          if self.bot.db["economy"][top_user]["prestige"] >= 5:
            msg += f"{count}. **[{pres_icon}:fire:] {bot.get_user(int(top_user))}**: **{top_bal}{coin}** \n"
          elif self.bot.db["economy"][top_user]["prestige"] < 5:
            msg += f"{count}. **[{pres_icon}] {bot.get_user(int(top_user))}**: **{top_bal}{coin}** \n"
        else: 
          msg += f"{count}. [{pres_icon}] {bot.get_user(int(top_user))}: **{top_bal}{coin}** \n"
        ecoLB.pop(str(top_user))
        if ecoLB != {}:
          top_bal = max(ecoLB.values())
          top_user = list(ecoLB.keys())[list(ecoLB.values()).index(max(ecoLB.values()))]
        elif ecoLB == {}:
          top_user = "No one here, "
          top_bal = f"do `{self.bot.prefix}help economy` to see avaliable commands!"
        count += 1
      else:
        msg += f"{count}. {top_user} {top_bal} \n"
        count +=1


    new_embed = discord.Embed(
      title = "Coins Leaderboard", 
      description = msg, 
      color = discord.Color.green()
    )
    new_embed.set_footer(text = f"Use {self.bot.prefix}lb for kitkats leaderboard")
    await old.edit(embed = new_embed)
  elif lb == "bug" or lb == "bugs" or lb == "b":
    buglb = {}
    embed = discord.Embed(
      title = "Bugs Leaderboard", 
      description = "Getting leaderboard...",
      color = discord.Color.blue()
    )
    old = await ctx.reply(embed = embed)
    msg = ""
    count = 1
    for i in self.bot.dbo["others"]["bugs"]:
      buglb[i] = self.bot.dbo["others"]["bugs"][i]
    if buglb != {}:
      top_bal = max(buglb.values())
      top_user = list(buglb.keys())[list(buglb.values()).index(max(buglb.values()))]
      msg += f"{count}. {bot.get_user(int(top_user))}: `{top_bal}` \n"
      buglb.pop(str(top_user))
      
    else:
      top_user = "No one here, "
      top_bal = f"report bugs by joining the official KitkatBot server. Use `{self.bot.prefix}discord` to join!"
      msg += f"{count}. {top_user}: `{top_bal}` \n"

    
    while count < 5:
      count += 1
      if buglb != {}:
        top_bal = max(buglb.values())
        top_user = list(buglb.keys())[list(buglb.values()).index(max(buglb.values()))]
        msg += f"{count}. {bot.get_user(int(top_user))}: `{top_bal}` \n"
        buglb.pop(str(top_user))
      elif buglb == {}:
        top_user = "No one here, "
        top_bal = f"report bugs in the official KitkatBot server! (`{self.bot.prefix}discord`)"
        msg += f"{count}. {top_user} {top_bal} \n"

    members = 0
    for a in self.bot.dbo["others"]["bugs"]:
      members += self.bot.dbo["others"]["bugs"][a]
    new_embed = discord.Embed(
      title = "Bugs Leaderboard", 
      description = msg + f"A total of `{members}` bugs have been reported!", 
      color = discord.Color.green()
    )
    new_embed.set_footer(text = f"Report bugs by joining the official KitkatBot server. Use {self.bot.prefix}discord to join!")
    await old.edit(embed = new_embed)
  elif lb == "s" or lb == "sponsor" or lb == "sponsors":
    buglb = {}
    embed = discord.Embed(
      title = "Sponsor Leaderboard", 
      description = "Getting leaderboard...",
      color = discord.Color.blue()
    )
    old = await ctx.reply(embed = embed)
    msg = ""
    count = 1
    for i in self.bot.db["economy"]:
      buglb[i] = self.bot.db["economy"][i]["sponsor"]
    if buglb != {}:
      top_bal = max(buglb.values())
      top_user = list(buglb.keys())[list(buglb.values()).index(max(buglb.values()))]
      msg += f"{count}. {bot.get_user(int(top_user))}: **{top_bal}{coin}** \n"
      buglb.pop(str(top_user))
      
    else:
      top_user = "No one here, "
      top_bal = f"sponsor giveaways by creating a ticket in the official KitkatBot server. Use `{self.bot.prefix}discord` to join!"
      msg += f"{count}. {top_user}: `{top_bal}` \n"

    
    while count < 5:
      count += 1
      if buglb != {}:
        top_bal = max(buglb.values())
        top_user = list(buglb.keys())[list(buglb.values()).index(max(buglb.values()))]
        msg += f"{count}. {bot.get_user(int(top_user))}: **{top_bal}{coin}** \n"
        buglb.pop(str(top_user))
      elif buglb == {}:
        top_user = "No one here, "
        top_bal = f"sponsor giveaways by creating a ticket in the official KitkatBot server! (`{self.bot.prefix}discord`)"
        msg += f"{count}. {top_user} {top_bal} \n"

    members = 0
    for a in self.bot.db["economy"]:
      members += self.bot.db["economy"][a]["sponsor"]
    new_embed = discord.Embed(
      title = "Sponsor Leaderboard", 
      description = msg + f"A total of **{members}{coin}** have been sponsored!", 
      color = discord.Color.green()
    )
    new_embed.set_footer(text = f"Sponsor giveaways by joining the official KitkatBot server. Use {self.bot.prefix}discord to join!")
    await old.edit(embed = new_embed)

@leaderboard.error
async def leaderboard_error(ctx, error):
  await ctx.send(str(error))
  await ctx.send(traceback.format_exc())

@bot.command()
async def lottery(ctx, time=None, *, price : int=None):
  if ctx.author.id == 915156033192734760:
    lottery_channel = 924492712328171530
    lottery_role = 924492846550114365
    if time is None:
        return await ctx.send(
            f"Please enter a time and a prize! `({self.bot.prefix}lottery <time> <prize> | s = seconds, m = minutes, h = hours, d = days`)"
        )
    elif price is None:
        await ctx.send(
            f"Please enter a prize! (`{self.bot.prefix}gcreate <time> <prize>`)"
        )

    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    lottery_time = int(time[:-1]) * time_convert[time[-1]]
    ends = int(_time.time()) + lottery_time
    embed = discord.Embed(
        title="Lottery Posted!",
        description=
        f"Your lottery was posted in <#{lottery_channel}>",
        color=discord.Color.blue())
    embed.set_author(name=ctx.message.author,
                      url=ctx.author.avatar_url,
                      icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)
    embed = discord.Embed(
        title=f"Lottery",
        description=
        f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{ends}:R> | <t:{ends}> \nCurrent prize pool: `No one has bought a ticket!` \nCost: {price}{coin}",
        color=discord.Color.green())
    embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
    lottery_msg = await ctx.guild.get_channel(lottery_channel).send(f"<@&{lottery_role}>", embed=embed)
    await lottery_msg.add_reaction("🎟️")

    count = 0
    while count < lottery_time:
      count += 60
      users = 0
      channel_posted = ctx.guild.get_channel(lottery_channel)
      new_lottery_msg = await channel_posted.fetch_message(lottery_msg.id)
      user_list = [
        u for u in await new_lottery_msg.reactions[0].users().flatten()
        if u != bot.user
      ]
      user_list_copy = user_list.copy()
      for i in user_list_copy:
        if self.bot.db["economy"][str(i.id)]["balance"] >= price:
          users += 1
          user_list.remove(i)
      if users <= 1:
        new_embed = discord.Embed(
        title=f"Lottery",
        description=
        f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{ends}:R> | <t:{ends}> \nCurrent prize pool: `Not enough tickets purchased!` \nCost: {price}{coin} \nNumber of tickets bought: `{users}`",
        color=discord.Color.green())
        new_embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
      else:
        new_embed = discord.Embed(
        title=f"Lottery",
        description=
        f"React with :tickets: to purchase a lottery ticket! The cost will be deducted from your balance right before the lottery ends! \nEnds: <t:{ends}:R> | <t:{ends}> \nCurrent prize pool: **{users * price}{coin}** \nCost: **{price}{coin}** \nNumber of tickets bought: `{users}`",
        color=discord.Color.green())
        new_embed.set_footer(text = "If you do not have enough money, your entry will not be registered!")
      
      await new_lottery_msg.edit(embed = new_embed)
      await asyncio.sleep(60)

    channel_posted = ctx.guild.get_channel(lottery_channel)
    new_lottery_msg = await channel_posted.fetch_message(lottery_msg.id)
    user_list = [
        u for u in await new_lottery_msg.reactions[0].users().flatten()
        if u != bot.user
    ]
    user_list_copy = user_list.copy()
    for i in user_list_copy:
      if self.bot.db["economy"][str(i.id)]["balance"] <= price:
        user_list.remove(i)
    if len(user_list) <= 1:
        await lottery_msg.reply("Not enough people joined the lottery.")
    else:
        winner = random.choice(user_list)
        for user in user_list:
          self.bot.db["economy"][str(user.id)]["balance"] -= price
        prize = len(user_list) * price
        await lottery_msg.reply(f"{winner.mention} has won **{prize}{coin}**! (Tickets purchased: {len(user_list)})")
        self.bot.db["economy"][str(winner.id)]["balance"] += prize
        channel_posted = ctx.guild.get_channel(lottery_channel)
        new_lottery_msg = await channel_posted.fetch_message(lottery_msg.id)
        final_embed = discord.Embed(
        title=f"Lottery",
        description=
        f"The lottery ended <t:{ends}:R> | <t:{ends}>! \nPrize pool: **{users * price}{coin}** \nWinner: `{winner}` \nNumber of tickets bought: `{users}`",
        color=discord.Color.green())
        await new_lottery_msg.edit(embed = final_embed)

@lottery.error
async def lottery_error(ctx, error):
    await ctx.send(str(error))



@bot.command(aliases = ["pet"])
async def pets(ctx, arg = None, *,arg2 = None):
  if str(ctx.author.id) in self.bot.db["economy"]:
    if arg is None: 
      if self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"] == "":
        embed = discord.Embed(
          title = "Pets", 
          description = f"Looks like you do not own a pet... Do `{self.bot.prefix}pet list` to see the avaliable pets!", 
          color = discord.Color.blue()
        )
      elif self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"] != "":
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
      await ctx.reply(embed = embed)
    elif arg == "list" or arg == "view":
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
      await ctx.reply(embed = embed)
    if arg == "buy" or arg == "purchase":
      if arg2 == "dog" or arg2 == "cat" or arg2 == "hamster":
        if self.bot.db["economy"][str(ctx.author.id)]["balance"] >= 50000:
          embed = discord.Embed(
            title = f"Pet: {arg2}", 
            description = f"React with a :white_check_mark: to buy a **{arg2}** \n**Warning:** This purchase will abandon your previous pet (if any) and reset it's level", 
              colour = discord.Color.blue()
              )
          pet_confirm = await ctx.send(embed = embed)

          await pet_confirm.add_reaction("✅")

          def check(reaction, user):
              return user.id == ctx.author.id and reaction.message == pet_confirm and str(reaction.emoji) in ["✅"]
          try:
              reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
              if str(reaction.emoji) == "✅":
                  self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"] = arg2
                  self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"] = f"{str(ctx.author.name)}'s pet"
                  self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] = 1
                  self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] = 1
                  self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] = 1
                  self.bot.db["economy"][str(ctx.author.id)]["balance"] -= 50000


                  new_embed = discord.Embed(
                      title=f"Pet",
                      description=f"You have successfully bought a `{arg2}`! To rename it, use `{self.bot.prefix}pet name <name>`. You can do `{self.bot.prefix}hunt` to get free coins!",
                      color=discord.Color.green())
                  await pet_confirm.edit(embed=new_embed)

          except asyncio.TimeoutError:
              await ctx.reply("You did not react in time!")
        elif self.bot.db["economy"][str(ctx.author.id)]["balance"] < 50000:
          await ctx.reply(f"You do not have enough coins to buy a {arg2}! Do `{self.bot.prefix}pet list` to view the requirements and cost!")

      elif arg2 in ("CookieMonster", "cookiemonster", "monkey", "lion", "tiger"):
        if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 1:
          if self.bot.db["economy"][str(ctx.author.id)]["balance"] >= 100000:
            embed = discord.Embed(
              title = f"Pet: {arg2}", 
              description = f"React with a :white_check_mark: to buy a **{arg2}** \n**Warning:** This purchase will abandon your previous pet (if any) and reset it's level", 
                colour = discord.Color.blue()
                )
            pet_confirm = await ctx.send(embed = embed)

            await pet_confirm.add_reaction("✅")

            def check(reaction, user):
                return user.id == ctx.author.id and reaction.message == pet_confirm and str(reaction.emoji) in ["✅"]
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "✅":
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"] = arg2
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"] = f"{str(ctx.author.name)}'s pet"
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] = 1
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] = 2
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] = 1
                    self.bot.db["economy"][str(ctx.author.id)]["balance"] -= 100000


                    new_embed = discord.Embed(
                        title=f"Pet",
                        description=f"You have successfully bought a `{arg2}`! To rename it, use `{self.bot.prefix}pet name <name>`. You can do `{self.bot.prefix}hunt` to get free coins!",
                        color=discord.Color.green())
                    await pet_confirm.edit(embed=new_embed)

            except asyncio.TimeoutError:
                await ctx.reply("You did not react in time!")
          elif self.bot.db["economy"][str(ctx.author.id)]["balance"] < 100000:
            await ctx.reply(f"You do not have enough coins to buy a {arg2}! Do `{self.bot.prefix}pet list` to view the requirements and cost!")
        elif self.bot.db["economy"][str(ctx.author.id)]["prestige"] < 1:
          await ctx.reply(f"Your prestige level is not high enough to buy a {arg2}! Do `{self.bot.prefix}pet list` to view the requirements and cost!")


      elif arg2 in ("bee", "python", "seal", "eagle"):
        if self.bot.db["economy"][str(ctx.author.id)]["prestige"] >= 2:
          if self.bot.db["economy"][str(ctx.author.id)]["balance"] >= 200000:
            embed = discord.Embed(
              title = f"Pet: {arg2}", 
              description = f"React with a :white_check_mark: to buy a **{arg2}** \n**Warning:** This purchase will abandon your previous pet (if any) and reset it's level", 
                colour = discord.Color.blue()
                )
            pet_confirm = await ctx.send(embed = embed)

            await pet_confirm.add_reaction("✅")

            def check(reaction, user):
                return user.id == ctx.author.id and reaction.message == pet_confirm and str(reaction.emoji) in ["✅"]
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "✅":
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["type"] = arg2
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"] = f"{str(ctx.author.name)}'s pet"
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] = 1
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] = 3
                    self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] = 1
                    self.bot.db["economy"][str(ctx.author.id)]["balance"] -= 200000


                    new_embed = discord.Embed(
                        title=f"Pet",
                        description=f"You have successfully bought a `{arg2}`! To rename it, use `{self.bot.prefix}pet name <name>`. You can do `{self.bot.prefix}hunt` to get free coins!",
                        color=discord.Color.green())
                    await pet_confirm.edit(embed=new_embed)

            except asyncio.TimeoutError:
                await ctx.reply("You did not react in time!")
          elif self.bot.db["economy"][str(ctx.author.id)]["balance"] < 200000:
            await ctx.reply(f"You do not have enough coins to buy a {arg2}! Do `{self.bot.prefix}pet list` to view the requirements and cost!")
        elif self.bot.db["economy"][str(ctx.author.id)]["prestige"] < 2:
          await ctx.reply(f"Your prestige level is not high enough to buy a {arg2}! Do `{self.bot.prefix}pet list` to view the requirements and cost!")
      else: 
        await ctx.reply(f"Invalid name! Use `{self.bot.prefix}pet list` to view the pets!")
    elif arg in ("upgrade", "up"):
      if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] > 0:
        base_upgrade = 10000
        upgrades_mult = 1.7
        pet_level = self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"]
        upgrade_cost = math.floor(base_upgrade * upgrades_mult ** pet_level)
        balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
        tier = self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"]
        name = self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"]
        if tier == 1 and pet_level >= 3:
          await ctx.reply(f"Your pet is tier 1 and it can only be upgraded to level 3. Do `{self.bot.prefix}pet list` to view pets in higher tier!")
        elif tier == 2 and pet_level >= 5:
          await ctx.reply(f"Your pet is tier 2 and it can only be upgraded to level 5. Do `{self.bot.prefix}pet list` to view pets in higher tier!")
        elif tier == 3 and pet_level >= 10:
          await ctx.reply(f"Your pet is tier 3 and it can only be upgraded to level 10. Do `{self.bot.prefix}pet list` to view pets in other tier!")
        else:
          if balance >= upgrade_cost:
            self.bot.db["economy"][str(ctx.author.id)]["balance"] -= upgrade_cost
            self.bot.db["economy"][str(ctx.author.id)]["pets"]["level"] += 1
            await ctx.reply(f"**{name}** has been upgraded to level {pet_level + 1}!")
          elif balance < upgrade_cost:
            await ctx.reply(f"You need **{upgrade_cost}{coin}** to upgrade your pet but you only have **{balance}{coin}**")
      else:
        await ctx.reply("You do not have a pet!")
    elif arg == "name":
      if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] > 0:
        if arg2 is not None:
          if len(arg2) <= 16:
            if "@everyone" in arg2 or "@here" in arg2 or "discord.gg" in arg2:
              await ctx.reply("Nice try but KitkatBot cannot be fooled! Try naming your pet something else!")
            else: 
              if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] > 0:
                self.bot.db["economy"][str(ctx.author.id)]["pets"]["name"] = arg2
                await ctx.reply(f"You have successfully renamed your pet to `{arg2}`")
              else: 
                await ctx.reply(f"You do not own a pet! Do `{self.bot.prefix}pet list` to view the avaliable pets!")
          else:
            await ctx.reply("Please make sure your pet's name does not exceed 16 characters!")
        else:
          await ctx.reply(f"Please use `{self.bot.prefix}pet name <name>` to name your pet!")
  else:
    await ctx.reply(f"Looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!") 

@bot.command(aliases = ["h"])
async def hunt(ctx):
  if str(ctx.author.id) in self.bot.db["economy"]:
    if self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] > 0:
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
      if int(_time.time()) >= self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] + cooldown:
        self.bot.db["economy"][str(ctx.author.id)]["balance"] += amt_of_coins
        self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] = _time.time()
        await ctx.reply(f"**{name}** went out hunting and brought back **{amt_of_coins}{coin}!** You can upgrade your pet using `{self.bot.prefix}pet upgrade`.")

      elif _time.time() < self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"] + cooldown:
        current_time = int(_time.time())
        last_hunt = self.bot.db["economy"][str(ctx.author.id)]["pets"]["last_hunt"]
        mins_left = str(math.floor((mins_ - ((current_time - last_hunt) % 3600) / 60)))
        secs_left = str(math.floor((60 - ((current_time - last_hunt) % 3600) % 60)))
        await ctx.reply(f"**{name}** just went out to hunt and needs to rest! **{name}** will be ready to hunt again in `{mins_left}m {secs_left}s`")
    elif self.bot.db["economy"][str(ctx.author.id)]["pets"]["tier"] == 0:
      await ctx.reply(f"You do not have a pet! Please do `{self.bot.prefix}pet list` to view the avaliable pets.")
  else: 
    await ctx.reply(f"Looks like you do not own a factory... Do `{self.bot.prefix}start` to built one!")

@bot.command(aliases = ["f"])
async def fish(ctx):
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

    if _time.time() >= self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] + cooldown:
      luck = random.randint(1,100)
      if luck > 30:
        self.bot.db["economy"][str(ctx.author.id)]["balance"] += money
        self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] = int(_time.time())
        embed = discord.Embed(
          title = "Fishing", 
          description = f"You went fishing and caught a wallet! You got **{money}{coin}**.", 
          color = discord.Color.green()
        )
        await ctx.reply(embed = embed)
      else:
        self.bot.db["economy"][str(ctx.author.id)]["balance"] -= money
        self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] = int(_time.time())
        embed = discord.Embed(
          title = "Fishing", 
          description = f"You went fishing and fished out a scuba diver! You got fined **{money}{coin}**", 
          color = discord.Color.red()
        )
        await ctx.reply(embed = embed)
        if self.bot.db["economy"][str(ctx.author.id)]["balance"] < 0:
          self.bot.db["economy"][str(ctx.author.id)]["balance"] = 0
    elif _time.time() < self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"] + cooldown:
        current_time = int(_time.time())
        last_fish = self.bot.db["economy"][str(ctx.author.id)]["fish"]["last_fish"]
        mins_left = str(math.floor((mins_ - ((current_time - last_fish) % 3600) / 60)))
        secs_left = str(math.floor((60 - ((current_time - last_fish) % 3600) % 60)))
        embed = discord.Embed(
          title = "Fishing", 
          description = f"You cannot fish so soon! You can fish again in `{mins_left}m {secs_left}s`", 
          color = discord.Color.orange()
        )
        await ctx.reply(embed = embed)
  else:
    await ctx.reply(f"Whoops, looks like you do not own a factory... Do `{self.bot.prefix}start` to build one!")

@bot.command(aliases = ["c", "treasure", "chests", "treasurechest"])
async def chest(ctx, arg = None):
  if str(ctx.author.id) in self.bot.db["economy"]:
    chests = self.bot.db["economy"][str(ctx.author.id)]["chests"]
    
    if arg is None:
      embed = discord.Embed(
        title = "Treasure Chests",
        description = f"You currently have `{chests}` treasure chests.\nTo open chests, you can do `{self.bot.prefix}chest open`. \nTo view the loot available, do `{self.bot.prefix}chest loot`. \n\nGet more treasure chests by using commands like `{self.bot.prefix}fish`, `{self.bot.prefix}hunt` and joining giveaways in the official KitkatBot server! (`{self.bot.prefix}discord`) \n*Note: This feature is still a work in progress and is not enabled yet!*",
        color = discord.Color.green()
      )
      embed.set_thumbnail(url="https://www.kindpng.com/picc/m/500-5006925_simple-treasure-chest-cartoon-hd-png-download.png")
      await ctx.reply(embed = embed)
    elif arg == "open":
      if chests > 0:
        ''''
      self.bot.db["economy"][str(ctx.author.id)]["chests"] -= 1
      looted = False
      while not looted:
        rarity = random.randint(1, 4)
        item = random.randint(1, 4)
        if rarity == 1:
          if item == 1:
            prize = f"small bag of coins (10,000{coin})"
            self.bot.db["economy"][str(ctx.author.id)]["balance"] += 10000
          if item == 2:
            prize = f"medium bag of coins (100,000{coin})"
            self.bot.db["economy"][str(ctx.author.id)]["balance"] += 100000
          if item == 3:
            prize = "capacity upgrade"
            self.bot.db["economy"][str(ctx.author.id)]["upgrade_cap"] += 10
          if item == 4:
            prize = "storage upgrade"
            self.bot.db["economy"][str(ctx.author.id)]["storage"] += self.bot.db["economy"][str(ctx.author.id)]["storage"] * 2
          looted = True
        if rarity == 2:
          if item == 1:
            prize = f"worker upgrade"
            self.bot.db["economy"][str(ctx.author.id)]["workers"] += 1
            looted = True
          if item == 2:
            prize = f"machine upgrade"
            self.bot.db["economy"][str(ctx.author.id)]["machine_level"] += 1
            looted = True
          if item == 3:
            if self.bot.db["economy"][str(ctx.author.id)]["rod_level"] < 3:
              prize = "rod upgrade"
              self.bot.db["economy"][str(ctx.author.id)]["rod_level"] += 1
            else:
              looted = False
          if item == 4:
            prize = "maxed out kitkat storage"
            self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = 1
            looted = True

        embed = discord.Embed(
          title = "Chest Reward",
          description = f"You opened a chest and got a **{prize}**",
          color = discord.Color.green()
        )
        await ctx.reply(embed = embed)
        '''
        await ctx.reply("Chests are still a work in progreess and is disabled for now!")
        
      else:
        await ctx.reply(f"You do not have any chests to open! Do `{self.bot.prefix}chest` for more information!")
    elif arg == "loot":
      embed = discord.Embed(
        title = "Chest Loot",
        description = f"""**Common:**
- Small bag of coins
- Medium bag of coins
- Capacity upgrade
- Storage upgrade

**Rare:**
- Worker upgrade
- Machine upgrade
- Rod upgrade
- Maxed out kitkat storage

**Epic:**
- 2 Chests
- 4 Chests
- Pet upgrade
- Daily cooldown reset

**Legendary:**
- Monthly cooldown reset
- Worker upgrade (2x)
- Machine upgrade (2x)
- Large bag of coins
""",
        color = discord.Color.green()
      )
      await ctx.reply(embed = embed)

@bot.command()
async def addchest(ctx, user:discord.Member, amt:int):
  chests = self.bot.db["economy"][str(user.id)]["chests"]
  if ctx.author.id == 915156033192734760:
    self.bot.db["economy"][str(user.id)]["chests"] += amt
    await ctx.reply(f"Added {amt} chest(s) to **{user}**. **{user.name}** now has {chests +  amt} chests!")

@bot.command(aliases = ["p", "pres"])
async def prestige(ctx):
  if str(ctx.author.id) in self.bot.db["economy"]:
    prestige = self.bot.db["economy"][str(ctx.author.id)]["prestige"]
    balance = self.bot.db["economy"][str(ctx.author.id)]["balance"]
    
    prestige_msg = f"""Welcome to the hall of prestiges! Here, you can view all the prestige perks and can unlock the option to prestige!

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


Current prestige: {prestige}
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
                self.bot.db["economy"][str(ctx.author.id)]["last_sold"] = int(_time.time())
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


@bot.command()
async def dropcode(ctx, channel : discord.TextChannel, code, amount : int):
  if ctx.author.id == 915156033192734760:
    embed = discord.Embed(
      title = "New Code Drop!",
      description = f"A KitkatBot code has appeared! \nCode: `{code}` \nReward: **{amount} {coin}** \nClaim the code using `{self.bot.prefix}redeem <code>`", 
      color = discord.Color.blurple()
    )
    embed.set_footer(text = "The code is only valid for one person. Good luck!")
    await channel.send(embed = embed)
    self.bot.dbo["others"]["code"][code] = amount
    await ctx.reply(f"Code created!")
    channel = bot.get_guild(923013388966166528).get_channel(968460468505153616)
    embed = discord.Embed(title = f"A code has been created.", description = f"Code: `{code}` \nAmount: **{amount} {coin}**", color = discord.Color.green())
    await channel.send(embed = embed)
  else:
    await ctx.reply(f"Only Kitkat3141 can create codes!")
@dropcode.error
async def dropcode_error(ctx, error):
  if ctx.author.id == 915156033192734760:
    await ctx.reply(f"Please use `{self.bot.prefix}dropcode <#channel> <code> <amount>`.")
  else:
    await ctx.reply("You do not have permission to create codes!")

@bot.command()
async def redeem(ctx, code = None):
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
    await ctx.reply(f"Looks like you do not own a factory! Do `{self.bot.prefix}start` to build one!")
  else:
    embed = discord.Embed(
      title = "Code not found...",
      description = f"This code has been redeemed before or does not exist... Sorry.",
      color = discord.Color.red()
    )
    await ctx.reply(embed = embed, mention_author = False)

@bot.command()
async def addmoney(ctx, user_: discord.Member, amt: int):
    if ctx.author.id == 915156033192734760:
        embed = discord.Embed(
            title=f"Economy",
            description=
            f"React with a ✅ to add **{amt}{coin}** to {user_.mention}!",
            color=discord.Color.red())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=60,
                                                check=check)
            # waiting for a reaction to be added - times out after x seconds, 60
            if str(reaction.emoji) == "✅":
                self.bot.db["economy"][str(user_.id)]["balance"] += amt
                new_embed = discord.Embed(
                    title=f"Economy",
                    description=f"Successfully added **{amt}{coin}**to {user_.mention}",
                    color=discord.Color.green())
                await msg.edit(embed=new_embed)

        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time.")

    else:
        await ctx.send(f"Only Kitkat3141 can rig the economy! Do `{self.bot.prefix}help economy` to see the economy commands!"
                       )

@bot.command()
async def removemoney(ctx, user_: discord.Member, amt: int):
    if ctx.author.id == 915156033192734760:
        embed = discord.Embed(
            title=f"Economy",
            description=
            f"React with a ✅ to remove **{amt}{coin}** from {user_.mention}!",
            color=discord.Color.red())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=60,
                                                check=check)
            # waiting for a reaction to be added - times out after x seconds, 60
            if str(reaction.emoji) == "✅":
                self.bot.db["economy"][str(user_.id)]["balance"] -= amt
                new_embed = discord.Embed(
                    title=f"Economy",
                    description=f"Successfully removed **{amt}{coin}** from {user_.mention}",
                    color=discord.Color.green())
                await msg.edit(embed=new_embed)

        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time.")

    else:
        await ctx.send(f"Only Kitkat3141 can rig the economy! Do `{self.bot.prefix}help economy` to see the economy commands!"
                       )


@bot.command()
async def reseteconomy(ctx, user: discord.Member = None):
    if ctx.author.id == 915156033192734760:
      if user is None:
        embed = discord.Embed(
            title=f"Economy Reset",
            description=
            f"React with a ✅ to reset the economy! \n**Warning**: This cannot be undone",
            color=discord.Color.red())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
            # This makes sure nobody except the command sender can interact with the "menu"

        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=60,
                                                check=check)
            # waiting for a reaction to be added - times out after x seconds, 60
            if str(reaction.emoji) == "✅":
                self.bot.db["economy"] = {}
                new_embed = discord.Embed(
                    title=f"Economy Reset",
                    description=f"The economy has been successfully resetted!",
                    color=discord.Color.green())
                await msg.edit(embed=new_embed)

        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time.")
      else:
        embed = discord.Embed(
            title=f"Economy Reset",
            description=
            f"React with a ✅ to reset the economy for {user.mention}! \n**Warning**: This cannot be undone",
            color=discord.Color.red())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message == msg and str(reaction.emoji) in ["✅"]
            # This makes sure nobody except the command sender can interact with the "menu"

        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=60,
                                                check=check)
            # waiting for a reaction to be added - times out after x seconds, 60
            if str(reaction.emoji) == "✅":
                self.bot.db["economy"].pop(str(user.id))
                new_embed = discord.Embed(
                    title=f"Economy Reset",
                    description=f"The economy has been successfully resetted for {user.mention}!",
                    color=discord.Color.green())
                await msg.edit(embed=new_embed)

        except asyncio.TimeoutError:
            await ctx.reply("You did not react in time.")
    else:
        await ctx.send(f"Only Kitkat3141 can reset the economy! Do you want to join the economy? Do `{self.bot.prefix}help economy` to see the economy commands!"
                       )

# DEV COMMANDS
@bot.command()
async def devdb(ctx, arg1=None, arg2=None):
    if ctx.message.author.id == 915156033192734760:
      self.bot.db["economy"]["427269999523004447"]["prestige"] = 4

@devdb.error
async def devdb_error(ctx, error):
    await ctx.send(traceback.format_exc())
    await ctx.send(str(error))

@bot.command()
async def blacklist(ctx, user : discord.Member = None):
  if ctx.message.author.id == 915156033192734760:
    self.bot.dbo["others"]["user_blacklists"].append(user.id)
    await ctx.reply(f"**{user}** has been blacklisted!")
  else:
    await ctx.reply("Only admins can blacklist users!")

@bot.command()
async def unblacklist(ctx, user : discord.Member = None):
  if ctx.message.author.id == 915156033192734760:
    self.bot.dbo["others"]["user_blacklists"].remove(user.id)
    await ctx.reply(f"**{user}** has been removed from the blacklist!")
  else:
    await ctx.reply("Only admins can remove users from the blacklist!")

@bot.command()
async def getguilds(ctx):
    if ctx.author.id == 915156033192734760:
        count = 0
        bot_guilds = ""
        embed = discord.Embed(title = "KitkatBot Guilds", description = "Getting guilds...", color = discord.Color.blue())
        msg = await ctx.send(embed = embed)
        for guild in bot.guilds:
          try:
            guild_invite = "None"
          except discord.HTTPException:
            guild_invite = "No permission."
          count = count + 1
          bot_guilds += f"{count}: {guild.name}, ID: {guild.id}, Shard ID: {guild.shard_id}, Chunked: {guild.chunked}, Member count: {guild.member_count}, Server Invite: {guild_invite} \n \n"
        new_embed = discord.Embed(title="KitkatBot Guilds",
                              description=bot_guilds,
                              color=discord.Color.green())
        await msg.edit(embed = new_embed)


@getguilds.error
async def getguilds_error(ctx, error):
    await ctx.send(str(error))

@bot.command()
async def guilds(ctx):
  if ctx.author.id == 915156033192734760:
        count = 0
        for guild in bot.guilds:
          count += 1
        await ctx.reply(f"KitkatBot is currently in `{count}` guilds!")

@bot.command()
async def leaveserver(ctx, server_id: int):
    if ctx.author.id == 915156033192734760:
        guild_id = bot.get_guild(server_id)
        await guild_id.leave()
        await ctx.send(
            f"Successfully left **{guild_id.name}** | `ID: {guild_id.id}`")


@leaveserver.error
async def leaveserver_error(ctx, error):
    await ctx.send(str(error))


@bot.command()
async def restart(ctx):
    if ctx.author.id == 915156033192734760:
        await ctx.send("Restarting bot... `This might take a few seconds`")
        guild = bot.get_guild(923013388966166528)
        log_id = guild.get_channel(927434363317157899)
        online_since = int(_time.time())
        ping = round(bot.latency * 1000)
        log_embed = discord.Embed(
          title = "KitkatBot Restarted",
          description = f"KitkatBot got restrted for the funni <t:{online_since}:R>. \nPing: `{ping}ms`",
          color = discord.Color.green()
        )
        await log_id.send(embed = log_embed)
        #    self.bot.db["restart_cmd"][ctx.guild.id] = ctx.channel.id
        os.execv(sys.executable, ['python'] + sys.argv)
    else: 
        await ctx.reply("Only KitkatBot admins are allowed to to restart the bot!")


@bot.command()
async def kill(ctx):
    if ctx.author.id == 915156033192734760:
        msg = await ctx.send("Stopping all processes...")
        await msg.edit(content="Killing bot...")
        await bot.close()
    else:
        await ctx.reply("Only KitkatBot admins are allowed to kill the bot!")


@bot.command()
async def serverblacklist(ctx, server_id):
    if ctx.author.id == 915156033192734760:
      if server_id in self.bot.dbo["others"]["server_blacklists"]:
        await ctx.send("That server is already blacklisted!")
      else:
        self.bot.dbo["others"]["server_blacklists"].append(server_id)
        server = bot.get_guild(int(server_id)).name
        guild_id = bot.get_guild(int(server_id))
        await guild_id.leave()
        embed = discord.Embed(title = "Server Blacklist!", description = f"Server: {server} \nServer ID: {server_id}")
        await ctx.send(embed = embed)
        
@bot.command()
async def serverunblacklist(ctx, server_id):
  if ctx.author.id == 915156033192734760:
      if server_id in self.bot.dbo["others"]["server_blacklists"]:
        self.bot.dbo["others"]["server_blacklists"].remove(server_id)
        await ctx.send(f"{server_id} has been removed from the blacklist!")

@bot.command()
async def bug(ctx, user:discord.Member=None):
  if user is None:
    if str(ctx.author.id) in self.bot.dbo["others"]["bugs"]:
      bugs = self.bot.dbo["others"]["bugs"][str(ctx.author.id)]
    else:
      bugs = 0
    await ctx.reply(f"You have found `{bugs}` bugs.")
  else:
    if str(user.id) in self.bot.dbo["others"]["bugs"]:
      bugs = self.bot.dbo["others"]["bugs"][str(user.id)]
    else:
      bugs = 0
    await ctx.reply(f"{user.name} has found `{bugs}` bugs.")
@bug.error
async def bug_error(ctx, error):
    await ctx.reply(str(error))

@bot.command()
async def addbug(ctx, user:discord.Member=None):
  if ctx.author.id == 915156033192734760:
    if str(user.id) in self.bot.dbo["others"]["bugs"]:
      self.bot.dbo["others"]["bugs"][str(user.id)] += 1
      bugs = self.bot.dbo["others"]["bugs"][str(user.id)]
      await ctx.reply(f"Updated **{user.name}**'s bug count. **{user.name}** has now found `{bugs}` bugs.")
    else:
      self.bot.dbo["others"]["bugs"][str(user.id)] = 1
      bugs = self.bot.dbo["others"]["bugs"][str(user.id)]
      await ctx.reply(f"Updated **{user.name}**'s bug count. **{user.name}** has now found `{bugs}` bugs.")

@bot.command()
async def removebug(ctx, user:discord.Member=None):
  if ctx.author.id == 915156033192734760:
    if str(user.id) in self.bot.dbo["others"]["bugs"]:
      self.bot.dbo["others"]["bugs"][str(user.id)] -= 1
      bugs = self.bot.dbo["others"]["bugs"][str(user.id)]
      await ctx.reply(f"Updated {user.name}'s bug count. {user.name} has now found `{bugs}` bugs.")
      if bugs <= 0:
        del self.bot.dbo["others"]["bugs"][str(user.id)]
    else:
      await ctx.reply(f"{user.name} has found 0 bugs!")

@bot.command()
async def sponsor(ctx, user:discord.Member=None):
  if user is None:
    if str(ctx.author.id) in self.bot.db["economy"]:
      sponsor = self.bot.db["economy"][str(ctx.author.id)]["sponsor"]
    else:
      sponsor = 0
    await ctx.reply(f"You have sponsored **{sponsor}{coin}!**")
  else:
    if str(user.id) in self.bot.db["economy"]:
      sponsor = self.bot.db["economy"][str(user.id)]["sponsor"]
    else:
      sponsor = 0
    await ctx.reply(f"{user.name} has sponsored a total of **{sponsor}{coin}!**")

@bot.command()
async def addsponsor(ctx, user:discord.Member, amt : int):
  if ctx.author.id == 915156033192734760:
    if str(user.id) in self.bot.db["economy"]:
      self.bot.db["economy"][str(user.id)]["sponsor"] += amt
      sponsor = self.bot.db["economy"][str(user.id)]["sponsor"]
      await ctx.reply(f"Updated {user.name}'s sponsored coins! {user.name} has now sponsored a total of **{sponsor}{coin}.**")
    else:
      ctx.reply(f"{user} does not own a factory!")

@bot.command()
async def nuke(ctx):
    if ctx.author.id == 915156033192734760:
        count = 5
        while count > 0:
            await ctx.send(f"Nuking server + banning ALL members in {count}...")
            await asyncio.sleep(1)
            count -= 1

        await ctx.send("GET TROLLED! :D")

@bot.command()
async def backup(ctx, arg=None):
  if ctx.author.id == 915156033192734760:
    if arg == "list":
      await ctx.message.delete()
      with open("backup.txt", "w") as backup:
        backup.truncate(0)
        backup.close()
      with open("backup.txt", "a") as backup:
        for user in self.bot.db["economy"]:
          data = self.bot.db["economy"][user]
          backup.write(f"\n{user} : {data}")
      await ctx.send(file=discord.File("backup.txt"))
      os.remove("backup.txt")
    elif arg is None:
      await ctx.message.delete()
      with open("backup.txt", "w") as backup:
        backup.truncate(0)
        data = self.bot.db["economy"]
        data2 = self.bot.dbo["others"]
        backup.write("Economy: \n" + str(data) + "\nOthers: \n" + str(data2) + "\nBackup Done!")
      await ctx.send(file=discord.File("backup.txt"))
      os.remove("backup.txt")
#  await ctx.send(traceback.format_exc())
# RUN
bot.run(os.environ['TOKEN'], reconnect = True)
