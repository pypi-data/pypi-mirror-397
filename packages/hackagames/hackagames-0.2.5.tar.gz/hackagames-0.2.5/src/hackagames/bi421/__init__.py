#!env python3
"""
HackaGame - Game - Single421 
"""
import sys

import warnings, hacka, random
from .. import py421
from . import d6, firstBot, shell

class GameSolo( py421.GameSolo ) :

    def __init__( self, randomSeed= True, xBox=0, yBox=0 ):
        super().__init__()
        self.setRandom(randomSeed)
        self.setBox(xBox, yBox)

    def setRandom(self, randomSeed):
        self._random= randomSeed
        if type(self._random) == int :
            random.seed( self._random )
            self._random= True
        return self

    def setBox(self, xBox, yBox=0):
        self._xBox= xBox
        self._yBox= yBox
        if self._xBox < 9 :
            self._xBox= 9 
        if self._yBox < 9 : 
            self._yBox= self._xBox
        return self

    def diceBox(self):
        return (self._xBox, self._yBox)

    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (an AbsGamel)
        gameElements= hacka.Pod( '421-Solo', [9, 9] )
        gameElements.append( hacka.Pod( 'Status', [ self.engine.turn() ], [ self.engine.currentScore() ] ) )

        # Get dices
        dices= [d for d in self.engine.dices()]
        if self._random :
            random.shuffle(dices)
        
        # draw dices image :
        if self.diceBox() == (9, 9):
            # Init :
            handimg= [ [] for i in range(9) ]
            # Copy dices :
            for d in dices :
                for line, handline in zip( d6.image(d), handimg ) :
                    handline+= line + [0]
            # reFrame :
            for i in range(len(handimg)) :
                handimg[i]= handimg[i][:-1]
        else:
            handimg= d6.floatingImage(dices)

        # Update gameElements :
        for handline in handimg :
            gameElements.append( hacka.Pod( 'Img', handline ) )
        return gameElements

class GameMaster( hacka.SequentialGameMaster ):
    def __init__( self, mode= "Solo" ):
        game= GameSolo( True, 11, 12 )
        super().__init__( game, game.numberOfPlayer() )

def command():
    from hacka.command import Command, Option

    cmd= Command( "play",
    [
        Option( "port", "p", default=1400 ),
        Option( "number", "n", 1, "number of games" )
    ],
    "Play to hackagames bi421 (No argument)" )

    # Process the command line: 
    cmd.process()
    if not cmd.ready() :
        print( cmd.help() )
        return False
    return cmd

def play():
    from .shell import PlayerShell
    from .firstBot import Bot as Opponent

    # Process the command line: 
    cmd= command()
    if not cmd :
        exit()

    # Start the player the command line: 
    gameMaster= GameMaster()
    gameMaster.launchLocal(  [PlayerShell()], cmd.option("number") )  

def launch():
    # Process the command line: 
    cmd= command()
    if not cmd :
        exit()

    # Start the player the command line: 
    gameMaster= GameMaster()
    gameMaster.launchOnNet( cmd.option("number"), cmd.option("port") )
