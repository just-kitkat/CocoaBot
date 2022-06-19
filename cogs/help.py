import discord
from vars import *
from itertools import starmap
from discord.ext import commands, menus

class HelpPageSource(menus.ListPageSource):
  def __init__(self, data, helpcommand):
      super().__init__(data, per_page=6)
      self.helpcommand = helpcommand

  def format_command_help(self, no, command):
      signature = self.helpcommand.get_command_signature(command)
      docs = self.helpcommand.get_command_brief(command)
      return f"{no}. {signature}\n{docs}"
  
  async def format_page(self, menu, entries):
      page = menu.current_page
      max_page = self.get_max_pages()
      starting_number = page * self.per_page + 1
      iterator = starmap(self.format_command_help, enumerate(entries, start=starting_number))
      page_content = "\n".join(iterator)
      embed = discord.Embed(
          title=f"Help Command[{page + 1}/{max_page}]", 
          description=page_content,
          color=0xffcccb
      )
      author = menu.ctx.author
      embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar)  # author.avatar in 2.0
      return embed

class Help_cmd(commands.MinimalHelpCommand):
  def get_command_brief(self, command):
    return command.short_doc or "Command is not documented."
  async def send_bot_help(self, mapping):
    all_commands = list(chain.from_iterable(mapping.values()))
    formatter = HelpPageSource(all_commands, self)
    menu = MyMenuPages(formatter, delete_message_after=True)
    await menu.start(self.context)

    
"""  async def send_command_help(self, command):
    embed = discord.Embed(title=self.get_command_signature(command))
    embed.add_field(name="Help", value=command.help)
    alias = command.aliases
    if alias:
        embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

    channel = self.get_destination()
    await channel.send(embed=embed)"""

"""  async def send_error_message(self, error):
    embed = discord.Embed(title="Error", description=error)
    channel = self.get_destination()
    await channel.send(embed=embed)"""

class Help(commands.Cog):
  def __init__(self, bot):
    self._original_help_command = bot.help_command
    attrs = {
      "name" : "help",
      "help" : "Shows a help page!",
      'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)
    }
    bot.help_command = Help_cmd(command_attrs = attrs)
    bot.help_command.cog = self

  def cog_unload(self):
    self.help_command = self._original_help_command
  
async def setup(bot):
 await bot.add_cog(Help(bot))