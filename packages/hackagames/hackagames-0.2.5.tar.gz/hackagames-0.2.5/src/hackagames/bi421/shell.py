"""
HackaGame player interface 
"""
import os
import hacka as hk
from . import d6

# Script
def connect() :
    player= PlayerShell()
    player.takeASeat()

class PlayerShell(hk.Player) :

    def __init__(self):
        super().__init__()
        self._horizon= -1
        self._score= 0
        self._dices= [[0]]
        
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gamePod):
        self._horizon= -1
        self._score= 0
        self._dicesImage= [[0]]
        # Reports:
        print( f'---\nWake-up 421')

    def perceive(self, gameState):
        # update the game state:
        imgSize= gameState.integer(1)
        self._horizon= gameState.child(1).integer(1)
        self._score= gameState.child(1).value(1)
        self._dicesImage= [
            line.integers() for line in gameState.children()[1:2+imgSize]
        ]
        # Reports:
        os.system("clear")
        print( d6.shell( self._dicesImage ) )
        print( f"Horizon: {self._horizon}\t| Score: {self._score}" )

    def decide(self):
        action = input('Enter your action: ')
        return hk.Pod(action)
    
    def sleep(self, result):
        print( f'---\ngame end\nresult: {result}')

# Script :
if __name__ == '__main__' :
    connect()