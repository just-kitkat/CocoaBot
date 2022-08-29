from discord.ext import commands
import discord
from discord import app_commands
import random
from vars import *
from errors import *

class TicTacToeRequest(discord.ui.View):
  def __init__(self, userID, opponent, *, timeout=120):
    self.userID = userID
    self.opponent = opponent
    self.value = None
    super().__init__(timeout=timeout)

  @discord.ui.button(label = "Accept", style = discord.ButtonStyle.success)
  async def accept_match(self, itx: discord.Interaction, button: discord.ui.Button):
    if itx.user.id == self.opponent:
      self.value = True
      self.stop()
      await itx.response.defer()
    else:
      await itx.response.send_message("This Tic Tac Toe request is not for you!", ephemeral = True)

  @discord.ui.button(label = "Cancel request", style = discord.ButtonStyle.danger)
  async def cancel_match(self, itx: discord.Interaction, button: discord.ui.Button):
    if itx.user.id == self.userID:
      self.value = False
      self.stop()
      await itx.response.defer()
    else:
      await itx.response.send_message("This Tic Tac Toe request is not for you!", ephemeral = True)

class TicTacToeButton(discord.ui.Button):
  def __init__(self, x: int, y: int):
    super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
    self.x = x
    self.y = y

  # Called when button pressed
  # Game logic
  async def callback(self, interaction: discord.Interaction):
    view: TicTacToe = self.view
    if view.turn != interaction.user.id:
      if view.turn in (view.p1, view.p2):
        await interaction.response.send_message("It is not your turn yet!", ephemeral=True)
      else:
        await interaction.response.send_message(f"This is not your match of Tic Tac Toe. Start a match using `{self.bot.prefix}ttt <@user>`", ephemeral=True)
    else:
      if view.current_player == view.X:
        self.style = discord.ButtonStyle.danger
        self.label = 'X'
        self.disabled = True
        view.board[self.y][self.x] = view.X
        view.current_player = view.O
        view.turn = view.p2
        content = f"It is now <@{view.p2}>'s turn"
      else:
        self.style = discord.ButtonStyle.success
        self.label = 'O'
        self.disabled = True
        view.board[self.y][self.x] = view.O
        view.current_player = view.X
        view.turn = view.p1
        content = f"It is now <@{view.p1}>'s turn"
  
      winner = view.check_board_winner()
      if winner is not None:
        if winner == view.X:
          content = f'<@{view.p1}> won!'
        elif winner == view.O:
          content = f'<@{view.p2}> won!'
        else:
          content = "It's a tie!"
        for child in view.children:
          child.disabled = True
  
        view.stop()
      embed = discord.Embed(title = "Tic Tac Toe", description = f"{view.match_msg}Status: **{content}**", color = green)
      await interaction.response.edit_message(embed=embed, view=view)
    

class TicTacToe(discord.ui.View):
  X = -1
  O = 1
  Tie = 2

  def __init__(self, p1, p2, turn, match_msg):
    super().__init__()
    self.p1 = p1 # rep userID Icon: X
    self.p2 = p2 # rep userID Icon: O
    self.turn = turn
    self.current_player = self.X if self.turn == self.p1 else self.O
    self.match_msg = match_msg
    self.board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]

    # Our board is made up of 3 by 3 TicTacToeButtons
    # The TicTacToeButton maintains the callbacks and helps steer
    # the actual game.
    for x in range(3):
      for y in range(3):
        self.add_item(TicTacToeButton(x, y))

  # This method checks for the board winner -- it is used by the TicTacToeButton
  def check_board_winner(self):
    for across in self.board:
      value = sum(across)
      if value == 3:
        return self.O
      elif value == -3:
        return self.X

    # Check vertical
    for line in range(3):
      value = self.board[0][line] + self.board[1][line] + self.board[2][line]
      if value == 3:
        return self.O
      elif value == -3:
        return self.X

    # Check diagonals
    diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
    if diag == 3:
      return self.O
    elif diag == -3:
      return self.X

    diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
    if diag == 3:
      return self.O
    elif diag == -3:
      return self.X

    # If we're here, we need to check if a tie was made
    if all(i != 0 for row in self.board for i in row):
      return self.Tie

    return None

class Games(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name = "tictactoe")
  async def tictactoe(self, itx: discord.Interaction, user:discord.Member):
    """Play Tic Tac Toe with a friend!"""
    title = "Tic Tac Toe"
    embed = discord.Embed(title = title, description = f"<@{itx.user.id}> has challenged you to a game of Tic Tac Toe!", color = discord.Color.blurple())
    view = TicTacToeRequest(itx.user.id, user.id)
    await itx.response.send_message(user.mention, embed = embed, view = view)
    await view.wait()
    if view.value:
      await itx.delete_original_response()
      turn = random.choice([itx.user.id, user.id])
      match_msg = f"{itx.user.mention} has challenged {user.mention} to a game of Tic Tac Toe! \n"
      embed = discord.Embed(title = title, description = f"{match_msg}Status: **It is now <@{turn}>'s turn!**", color = green)
      await itx.channel.send(embed = embed, view = TicTacToe(itx.user.id, user.id, turn, match_msg))
      
    elif view.value == False:
      embed = discord.Embed(title = "Tic Tac Toe", description = f"{itx.user.mention} has canceled the match against {user.mention}!", color = red)
      await itx.edit_original_response(embed = embed, view = None)
    else:
      embed = discord.Embed(title = "Tic Tac Toe", description = f"{user.mention} took too long to accept the match! To start a new game, use `/tictactoe`!", color = red)
      await itx.edit_original_response(embed = embed, view = None)

async def setup(bot):
  await bot.add_cog(Games(bot))