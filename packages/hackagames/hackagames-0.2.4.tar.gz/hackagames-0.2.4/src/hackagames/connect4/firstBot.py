"""
HackaGame player interface 
"""
import random
import hacka as hk
from .grid import Grid

# Script
def connect() :
    player= Bot()
    results= player.takeASeat()
    print( f"Average: {sum(results)/len(results)}" )

def log( anStr ):
    #print( anStr )
    pass

class Bot( hk.Player ):

    def __init__(self):
        super().__init__()
        self.grid= Grid()
        self.playerId= 0
        
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gamePod):
        self.playerId= playerId
        assert( gamePod.label() == 'Connect4')
        
    def perceive(self, gameState):
        # update the game state:
        self.grid.initializeFrom( gameState )
        
    def decide(self):
        options = self.grid.possibilities()
        action = random.choice( options )
        return hk.Pod(action)
    
    def sleep(self, result):
        log( f'---\ngame end on result: {result}')

# Script :
if __name__ == '__main__' :
    connect()