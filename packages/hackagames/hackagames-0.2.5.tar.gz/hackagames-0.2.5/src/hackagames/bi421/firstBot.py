#!env python3
"""
First Bot for 421
"""
import random, hacka
from . import d6

# script :
def connect() :
    bot= Bot()
    results= bot.takeASeat()
    print( f"\n## Statistics:\n\tAverage: { float(sum(results))/len(results) }" )

class Bot( hacka.Player ) :

    def __init__(self):
        super().__init__()
        self._horizon= -1
        self._score= 0
        self._dicesImage= [[0]]

    # Accessors :
    def horizon(self):
        return self._horizon

    def dices(self):
        return self._dicesImage
    
    def actions(self):
        return [ 'keep-keep-keep', 'keep-keep-roll', 'keep-roll-keep', 'keep-roll-roll',
            'roll-keep-keep', 'roll-keep-roll', 'roll-roll-keep', 'roll-roll-roll' ]
    
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        self._horizon= -1
        self._score= 0
        self._dicesImage= [[0]]

    def perceive(self, gameState):
        imgSize= gameState.integer(1)
        self._horizon= gameState.child(1).integer(1)
        self._score= gameState.child(1).value(1)
        self._dicesImage= [
            line.integers() for line in gameState.children()[1:2+imgSize]
        ]
        #print( d6.shell( self._dicesImage ) )

    def decide(self):
        return hacka.Pod( random.choice( self.actions() ) )

    def sleep(self, result):
        self._horizon= -1

# script :
if __name__ == '__main__' :
    connect()
