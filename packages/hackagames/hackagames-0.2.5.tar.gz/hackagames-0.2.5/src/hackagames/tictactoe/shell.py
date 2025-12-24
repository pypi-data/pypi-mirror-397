"""
HackaGame player interface 
"""
import os
import hacka as hk
from .grid import Grid

# Script
def connect() :
    player= PlayerShell()
    player.takeASeat()

class PlayerShell(hk.Player) :

    def __init__(self):
        super().__init__()
        self.grid= Grid()
        self.playerId= 0
        self.targets= [0] # The target area where the player can play. A list of number from 1 to 9
    
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gamePod):
        print(gamePod)
        game, mode= tuple( gamePod.label().split("-") )
        assert( game == 'TicTacToe')
        assert( mode in ['Classic', 'Ultimate'] )
        # Reports:
        print( f'---\nwake-up player-{playerId} ({numberOfPlayers} players)')
        print( game + ' ' + mode )
        # Attributes:
        self.mode= mode
        self.playerId= playerId
        self.end= 0              ## ???
        # Size
        letters= ["A", "B", "C"]
        numbers= range(1, 4)
        self.targets= [1]
        if mode == 'Ultimate' :
            letters= ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
            numbers= range(1, 10)
        # Initialize the grid
        self.grid= Grid()
        self.grid.initialize(letters, numbers)
    
    def perceive(self, gameState):
        # update the game state:
        self.grid.update( gameState.children()[:-1] )
        self.targets= gameState.children()[-1].integers()
        # Reports:
        os.system("clear")
        print( self )

    def decide(self):
        action = input('Enter your action: ')
        return hk.Pod( action )
    
    def sleep(self, result):
        print( f'---\ngame end\nresult: {result}')

    # Output :
    def __str__(self):
        targetStr=[ "", "ABC-123", "DEF-123", "GHI-123",
            "ABC-456", "DEF-456", "GHI-456",
            "ABC-789", "DEF-789", "GHI-789" ]
        
        # print the grid:
        s= self.grid.__str__(self.playerId)

        # print autorized actions:
        s+= "actions: "+ targetStr[ self.targets[0] ]
        for iGrid in self.targets[1:] :
            s+= ", "+ targetStr[iGrid]
        return s

# script :
if __name__ == '__main__' :
    connect()