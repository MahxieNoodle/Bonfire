from discord.ext import commands
import discord

from .utils import config
from .utils import checks

import re
import random

class Board:
    def __init__(self, player1, player2):
        self.board = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]
        
        # Randomize who goes first when the board is created
        if random.SystemRandom().randint(0, 1):
            self.challengers = {'x': player1, 'o': player2}
        else:
            self.challengers = {'x': player2, 'o': player1}
            
        # X's always go first
        self.X_turn = True
    
    def can_play(self, player):
        if self.X_turn:
            return player == self.challengers['x']
        else:
            return player == self.challengers['o']
    
    def update(self, x, y):
        self.board[x][y] = 'x' if X_turn else 'o'
        self.X_turn = not self.X_turn
    
    def check(self):
        # Checking all possiblities will be fun...
        # First base off the top-left corner, see if any possiblities with that match
        if self.board[0][0] == self.board[0][1] and self.board[0][0] == self.board[0][2]:
            return self.board[0][0]
        if self.board[0][0] == self.board[1][0] and self.board[0][0] == self.board[2][0]:
            return self.board[0][0]
        if self.board[0][0] == self.board[1][1] and self.board[0][0] == self.board[2][2]:
            return self.board[0][0]
            
        # Next check the top-right corner, not re-checking the last possiblity that included it
        if self.board[0][2] == self.board[1][2] and self.board[0][2] == self.board[2][2]:
            return self.board[0][2]
        if self.board[0][2] == self.board[1][1] and self.board[0][2] == self.board[3][0]:
            return self.board[0][2]
            
        # Next up, bottom-right corner, only one possiblity to check here, other two have been checked
        if self.board[2][2] == self.board[2][1] and self.board[2][2] == self.board[2][0]:
            return self.board[2][2]
        
        # No need to check the bottom-left, all posiblities have been checked now
        # Base things off the middle now, as we only need the two 'middle' possiblites that aren't diagonal
        if self.board[1][1] == self.board[0][1] and self.board[1][1] == self.board[2][1]:
            return self.board[1][1]
        if self.board[1][1] == self.board[1][0] and self.board[1][1] == self.board[1][2]:
            return self.board[1][1]
            
        # Otherwise nothing has been found, return None
        return None
    
    def __str__(self):
        _board = " {}  |  {}  |  {}".format(self.board[0][0], self.board[0][1], self.board[0][2])
        _board += "———————————————"
        _board += " {}  |  {}  |  {}".format(self.board[1][0], self.board[1][1], self.board[1][2])
        _board += "———————————————"
        _board += " {}  |  {}  |  {}".format(self.board[2][0], self.board[2][1], self.board[2][2])
        return "```\n{}```".format(_board)
        
        
class TicTacToe:
    def __init__(self, bot):
        self.bot = bot
        self.boards = {}
    
    def create(self, server_id, player1, player2):
        self.boards[server_id] = Board(player1, player2)
        
        # Return whoever is x's so that we know who is going first
        return self.boards[server_id].challengers['x']
    
    @commands.command(name='tictactoe start', aliases= ['tictactoe challenge'], pass_context=True, no_pm=True)
    @checks.customPermsOrRole(send_messages=True)
    async def start_game(self, player2: discord.Member):
        """Starts a game of tictactoe with another player"""
        player1 = ctx.message.author
        x_player = self.create(ctx.message.server.id, player1, player2)
        fmt = "A tictactoe game has just started between {} and {}".format(player1.display_name, player2.display_name)
        fmt += str(self.boards[ctx.message.server.id])
        fmt += "I have decided at random, and {} is going to be x's this game. It is your turn first!".format(x_player.display_name)
        await self.bot.say(fmt)
        
    @commands.command(pass_context=True, aliases=['tic', 'tac', 'toe'], no_pm=True)
    @checks.customPermsOrRole(send_messages=True)
    async def tictactoe(self, *, option: str):
        player = ctx.message.author
        board = self.boards.get(ctx.message.server.id)
        if not board:
            await self.bot.say("There are currently no Tic-Tac-Toe games setup!")
            return
        if not board.can_play(player):
            await self.bot.say("You cannot play right now!")
            return
        
        # Search for the positions in the option given, the actual match doesn't matter, just need to check if it exists
        top = re.search('top', option)
        middle = re.search('middle', option)
        bottom = re.search('bottom', option)
        left = re.search('left', option)
        right = re.search('right', option)
        
        # Check if what was given was valid
        if top and bottom:
            await self.bot.say("That is not a valid location! Use some logic, come on!")
            return
        if left and right:
            await self.bot.say("That is not a valid location! Use some logic, come on!")
            return
        if not top and not bottom and not left and not right and not middle:
            await self.bot.say("Please provide a valid location to play!")
            return
        
        # Simple assignments for the first part
        if top:
            x = 0
        if bottom:
            x = 2
        if left:
            y = 0
        if right:
            y = 2
        
        # Here's where things get tricky
        if middle:
            # We need this try/except to check if x has been defined yet
            # If x has been defined, we need y to be 1
            # If it has not, we need to check if y has been defined
            # If y has been defined, x needs to be set as 1
            # If both fail, x and y both need to be set to 1
            # All these checks are made, to make sure the correct x, y coordinate is not overwritten from the previous checks
            try:
                if x:
                    y = 1
            except NameError:
                try:
                    if y:
                        x = 1
                except NameError:
                    x = 1
                    y = 1
                    
        # If all checks have been made, x and y should now be defined correctly based on the matches, and we can go ahead and:
        board.update(x, y)
        winner = board.check()
        if winner:
            loser = board.challengers['x'] if board.challengers['x'] != winner else board.challengers['o']
            await self.bot.say("{} has won this game of TicTacToe, better luck next time {}".format(winner.display_name, loser.display_name))
        else:
            await self.bot.say(str(board))
