#!env python3
"""
First Bot for 421
"""
import random, hacka

# script :
def connect() :
    bot= Bot()
    results= bot.takeASeat()
    print( f"\n## Statistics:\n\tAverage: { float(sum(results))/len(results) }" )

def log( aString ):
    #print( aString )
    pass

class Bot( hacka.Player ) :

    def __init__(self):
        self._horizon= -1
        self._dices= [0, 0, 0]

    # Accessors :
    def horizon(self):
        return self._horizon

    def dices(self):
        return self._dices
    
    def actions(self):
        return [ 'keep-keep-keep', 'keep-keep-roll', 'keep-roll-keep', 'keep-roll-roll',
            'roll-keep-keep', 'roll-keep-roll', 'roll-roll-keep', 'roll-roll-roll' ]
    
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        self._horizon= -1
        self._dices= [0, 0, 0]

    def perceive(self, gameState):
        self._horizon= gameState.child(1).integer(1)
        self._dices= gameState.child(2).integers()
        self._score= gameState.child(2).value(1)

    def decide(self):
        return hacka.Pod( random.choice( self.actions() ) )

    def sleep(self, result):
        self._horizon= -1

# script :
if __name__ == '__main__' :
    connect()
