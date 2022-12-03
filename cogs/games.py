from discord.ext import commands
import discord
from discord import app_commands
import random
from vars import *
from errors import *
from dump.wordle_list import words, valid_words
import time
import copy

class WordleGuess(discord.ui.Modal, title='Wordle Guess'):
  value = False
  guess = discord.ui.TextInput(
    label='Guess',
    placeholder='Your guess here... ',
    min_length = 5,
    max_length = 5,
    required = True
  )
  async def on_submit(self, itx: discord.Interaction):
    if str(self.guess).lower() in valid_words+words:
      self.value = str(self.guess).upper()
      await itx.response.defer()
      self.stop()
    else:
      await itx.response.send_message("This word does not exist", ephemeral = True)

class WordleButton(discord.ui.View):
  def __init__(self, userID: int, itx: discord.Interaction, answer: str, guesses: int=6):
    self.userID = userID
    self.value = False
    self.guesses = guesses
    self.guessed = []
    self.answer = answer
    self.latest_itx = itx
    super().__init__(timeout=60*12)

  @discord.ui.button(label = "Guess a Word", style = discord.ButtonStyle.success)
  async def guess_wordle(self, itx: discord.Interaction, button: discord.ui.Button):
    wmodal = WordleGuess()
    await itx.response.send_modal(wmodal)
    await wmodal.wait()
    if wmodal.value != False:
      guess = wmodal.value
      for letter in guess:
        if letter not in self.guessed: self.guessed.append(letter)
      unused_letters = [":regional_indicator_" + chr(i) + ":" for i in range(ord('a'),ord('z')+1) if chr(i).upper() not in self.guessed]
      
      embed = (await (await itx.original_response()).fetch()).embeds[0]
      words_display = ""
      temp = {i: {"letter": guess[i], "color": "red"} for i in range(5)}
      temp_letters = [i for i in self.answer]
      for i in range(2):
        for index in temp:
          if temp[index]["letter"] == self.answer[index] and i == 0:
            temp[index]["color"] = "green"
            temp_letters.remove(temp[index]["letter"])
          if temp[index]["letter"] in self.answer and i == 1 and temp[index]["color"] == "red" and temp[index]["letter"] in temp_letters:
            temp[index]["color"] = "yellow"
            temp_letters.remove(temp[index]["letter"])
      words_display = ""
      for index in temp:
        words_display += f":regional_indicator_{temp[index]['letter'].lower()}: :{temp[index]['color']}_square: "
      embed.description = "\n".join(embed.description.split("\n")[:-2]) + f"\n{words_display}" + "\nUnused Letters: \n" + " ".join(unused_letters)
      self.guesses -= 1
      if guess == self.answer:
        embed.description += f"\n**You won! \nThe word was *{self.answer}***"
        self.value = True
        for child in self.children:
          child.disabled = True
        self.stop()
      elif self.guesses <= 0:
        embed.description += f"\n**You have lost! The word was *{self.answer}***"
        for child in self.children:
          child.disabled = True
        self.stop()
      await itx.edit_original_response(embed = embed, view = self)

  @discord.ui.button(label = "View Stats", style = discord.ButtonStyle.success)
  async def view_stats(self, itx: discord.Interaction, button: discord.ui.Button):
    await itx.response.send_message("Coming soon!", ephemeral = True)
  
  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      self.latest_itx = itx
      return True
    return await itx.client.itx_check(itx)

  async def on_timeout(self):
    for child in self.children:
      child.disabled = True
    embed = (await (await self.latest_itx.original_response()).fetch()).embeds[0]
    embed.description += f"\n**Answer: {self.answer} \nThis wordle game has timed out. Start a new one!**"
    await self.latest_itx.edit_original_response(embed=embed, view=self)

class Puzzle8Start(discord.ui.View):
  def __init__(self, userID):
    self.userID = userID
    self.value = False
    super().__init__(timeout=60*5)

  @discord.ui.button(label = "Start 3x3 Puzzle", style = discord.ButtonStyle.success)
  async def start_puzzle_3(self, itx: discord.Interaction, button: discord.ui.Button):
    self.value = 3
    self.stop()
    await itx.response.defer()
  @discord.ui.button(label = "Start 4x4 Puzzle", style = discord.ButtonStyle.success)
  async def start_puzzle_4(self, itx: discord.Interaction, button: discord.ui.Button):
    self.value = 4
    self.stop()
    await itx.response.defer()
  @discord.ui.button(label = "Start 5x5 Puzzle", style = discord.ButtonStyle.success)
  async def start_puzzle_5(self, itx: discord.Interaction, button: discord.ui.Button):
    self.value = 5
    self.stop()
    await itx.response.defer()

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

class Puzzle8Game(discord.ui.View):
  def __init__(self, userID, type_ = 3):
    self.userID = userID
    self.value = None
    self.moves = 0
    self.type_ = type_
    self.time_taken = time.time()
    self.pos_nums = [None, None, None,
      [1,2,3,4,5,6,7,8,-1],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,-1],
      [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,-1],
    ]
    super().__init__(timeout=60*10)
    while True:
      self.board = [copy.deepcopy([]) for i in range(type_)]
      nums = self.pos_nums[type_].copy()
      for y in range(type_):
        for x in range(type_):
          num = random.choice(nums)
          nums.remove(num)
          self.board[y].append(num)
          self.add_item(Puzzle8Button(userID, x, y, num))
      if self.isSolvable(self.board):
        break
      else:
        self.clear_items()
    

  def check_win(self):
    temp_board = []
    for row in self.board:
      for item in row:
        temp_board.append(item)
    return temp_board in self.pos_nums

  def move(self, t, c, i):
    if t == "up":
      self.board[i][c], self.board[i+1][c] = self.board[i+1][c], self.board[i][c]
    elif t == "down":
      self.board[i][c], self.board[i-1][c] = self.board[i-1][c], self.board[i][c]
    
    elif t == "left":
      self.board[i][c], self.board[i][c+1] = self.board[i][c+1], self.board[i][c]
    elif t == "right":
      self.board[i][c], self.board[i][c-1] = self.board[i][c-1], self.board[i][c]
    self.moves += 1
      

  def get_direction(self, x: int, y: int):
    direction = None
    for i in range(4):
      try:
        if i == 0 and self.board[y + 1][x] == -1: 
          direction = "up"; break
        if i == 1 and self.board[y - 1][x] == -1: 
          direction = "down"; break
        if i == 2 and self.board[y][x + 1] == -1: 
          direction = "left"; break
        if i == 3 and self.board[y][x - 1] == -1: 
          direction = "right"; break
      except Exception:
        pass
    return direction

  # Python3 program to check if a given instance of N*N-1
  # puzzle is solvable or not
  def getInvCount(self, arr):
  	arr1=[]
  	for y in arr:
  		for x in y:
  			arr1.append(x)
  	arr=arr1
  	inv_count = 0
  	for i in range(self.type_ * self.type_ - 1):
  		for j in range(i + 1,self.type_ * self.type_):
  			# count pairs(arr[i], arr[j]) such that
  			# i < j and arr[i] > arr[j]
  			if (arr[j] and arr[i] and arr[i] > arr[j]):
  				inv_count+=1
  	return inv_count
  # find Position of blank from bottom
  def findXPosition(self, puzzle):
  	# start from bottom-right corner of matrix
  	for i in range(self.type_ - 1,-1,-1):
  		for j in range(self.type_ - 1,-1,-1):
  			if (puzzle[i][j] == -1):
  				return self.type_ - i
  # This function returns true if given
  # instance of N*N - 1 puzzle is solvable
  def isSolvable(self, puzzle):
  	# Count inversions in given puzzle
  	invCount = self.getInvCount(puzzle)
  	# If grid is odd, return true if inversion
  	# count is even.
  	if (self.type_ & 1):
  		return ~(invCount & 1)
  	else: # grid is even
  		pos = self.findXPosition(puzzle)
  		if (pos & 1):
  			return ~(invCount & 1)
  		else:
  			return invCount & 1
          
class Puzzle8Button(discord.ui.Button):
  def __init__(self, userID, x: int, y: int, num: int):
    super().__init__(style=discord.ButtonStyle.secondary, label=num if num > 0 else '\u200b', row=y)
    self.userID = userID
    self.x = x
    self.y = y

  # Called when button pressed
  # Game logic
  async def callback(self, itx: discord.Interaction):
    view: Puzzle8Game = self.view
    direction = view.get_direction(self.x, self.y)
    if direction is not None:
      view.move(direction, self.x, self.y)
      #(row_index * row_length) + col_index
      for y_index, y in enumerate(view.board):
        for x_index, x in enumerate(y):
          view.children[(y_index * view.type_) + x_index].label = x if x != -1 else " "
      await itx.response.edit_message(view = view)  
      if view.check_win():
        for child in view.children:
          child.disabled = True
        pet_msg = ""
        if str(itx.user.id) in itx.client.db["economy"] and itx.client.db["economy"][str(itx.user.id)]["pets"]["tier"] != 0:
          pet_food = random.randint(1,4)
          itx.client.db["economy"][str(itx.user.id)]["pets"]["food"] += pet_food
          pet_msg = f"\nYou have recieved **{pet_food} pet food**!"
        time_taken = round(time.time() - view.time_taken, 2)
        if time_taken < itx.client.db["economy"][str(itx.user.id)]["games"]["sliding_puzzle_8_time"]: itx.client.db["economy"][str(itx.user.id)]["games"]["sliding_puzzle_8_time"] = time_taken
        if view.moves < itx.client.db["economy"][str(itx.user.id)]["games"]["sliding_puzzle_8_moves"]: itx.client.db["economy"][str(itx.user.id)]["games"]["sliding_puzzle_8_moves"] = view.moves
        embed = discord.Embed(title = "Sliding Puzzle 8", description = f"You win! \nMoves: **{view.moves}** \nTime taken: **{time_taken}s** {pet_msg}", color = blurple)
        await itx.edit_original_response(embed = embed, view = view)
        view.stop()
    else:
      await itx.response.send_message("Invalid Move!", ephemeral=True)
      
      

  async def interaction_check(self, itx: discord.Interaction):
    if self.userID == itx.user.id:
      return True
    return await itx.client.itx_check(itx)

class TicTacToeRequest(discord.ui.View):
  def __init__(self, userID, opponent, *, timeout=180):
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

  @app_commands.command(name = "slidingpuzzle")
  async def slidingpuzzle(self, itx: discord.Interaction):
    """Play a quick sliding puzzle game!"""
    fewest_moves = self.bot.db["economy"][str(itx.user.id)]["games"]["sliding_puzzle_8_moves"]
    best_time = self.bot.db["economy"][str(itx.user.id)]["games"]["sliding_puzzle_8_time"]
    if best_time == -1: fewest_moves, best_time = "No games yet", "No games yet"
    embed = discord.Embed(title = "Sliding Puzzle 8", description = f"Slide the number tiles into numerical order with the blank tile at the bottom right. \nBest Time: {best_time} \nFewest Moves: {fewest_moves} \n**Note: 5x5 does not work for mobile!**\nGood luck!", color = blurple)
    view = Puzzle8Start(itx.user.id)
    await itx.response.send_message(embed = embed, view = view)
    await view.wait()
    if view.value != False:
      embed = discord.Embed(title = "Sliding Puzzle 8", description = "Slide the number tiles into numerical order with the blank tile at the bottom right. \nBest Time: WIP \nGood luck!", color = blurple)
      view = Puzzle8Game(itx.user.id, view.value)
      await itx.edit_original_response(embed = embed, view = view)

  @app_commands.command(name = "wordle")
  async def wordle(self, itx: discord.Interaction):
    """Play a game of wordle!"""
    answer = random.choice(words).upper()
    all_letters = [":regional_indicator_" + chr(i) + ":" for i in range(ord('a'),ord('z')+1)]
    embed = discord.Embed(
      title = "Wordle",
      description = f"""
Guess the correct word to win!
{red_square}: Letter is not in the word
{yellow_square}: Correct letter but wrong position
{green_square}: Correct letter and correct position
\u200b
Unused Letters: 
{' '.join(all_letters)}
""",
      color = blurple
    )
    view = WordleButton(itx.user.id, itx, answer)
    await itx.response.send_message(embed = embed, view = view)
    await view.wait()
      

async def setup(bot):
  await bot.add_cog(Games(bot))