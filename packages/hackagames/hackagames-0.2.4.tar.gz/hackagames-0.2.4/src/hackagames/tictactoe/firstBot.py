#!env python3
"""
HackaGame player interface 
"""
import random
import hacka as hk
from .grid import Grid

def connect() :
    player= Bot()
    player.takeASeat()

class Bot(hk.Player) :
    def __init__(self):
        self.grid= Grid()
        self.playerId= 0
        self.possibilities= [0]
    
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gamePod ):
        assert( gamePod.label() in ['TicTacToe-Classic', 'TicTacToe-Ultimate'] )
        self.playerId= playerId
        # Initialize the grid
        self.grid= Grid( gamePod.label().split('-')[1] )
        self.possibilities= [1]

    def perceive(self, gameState):
        # Update the grid:
        self.grid.update( gameState.children()[:-1] )
        self.possibilities= gameState.children()[-1].integers()

    def decide(self):
        # Get all actions
        actions= self.listActions()
        # Select one 
        return hk.Pod( random.choice( actions ) )
    
    #def sleep(self, result):
        #print( f'---\ngame end\nresult: {result}')
    
    # TTT player :
    def listActions(self) :
        return self.grid.possibleActions( self.possibilities )
        
    def __str__(self):
        posStr=[ "", "A:C-1:3", "D:F-1:3", "G:I-1:3",
            "A:C-4:6", "D:F-4:6", "G:I-4:6",
            "A:C-7:9", "D:F-7:9", "G:I-7:9"]

        # print the grid:
        s= self.grid.__str__(self.playerId)

        # print autorized actions:
        s+= "actions: "+ posStr[ self.possibilities[0] ]
        for iGrid in self.possibilities[1:] :
            s+= ", "+ posStr[iGrid]
        return s
# Script :
if __name__ == '__main__' :
    connect()
