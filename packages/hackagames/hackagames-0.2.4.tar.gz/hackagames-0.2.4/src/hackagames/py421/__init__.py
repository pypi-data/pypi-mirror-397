#!env python3
"""
HackaGame - Game - Single421 
"""
import sys

import warnings, hacka
from . import engine as ge, firstBot

class GameSolo( hacka.AbsGame ) :

    # Accessors: 
    def numberOfPlayer(self):
        return 1
    
    # Game interface :
    def initialize(self):
        # Initialize a new game (not returning anything)
        self.engine= ge.Engine421()
        self.engine.initialize()
        self.score= 0
        return hacka.Pod().initialize( '421-Solo' )
    
    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (an AbsGamel)
        gameElements= hacka.Pod().initialize( '421-Solo' )
        gameElements.append( hacka.Pod().initialize( 'Horizon', [ self.engine.turn() ] ) )
        gameElements.append( hacka.Pod().initialize( 'Dices',
                                        self.engine.dices(),
                                        [ self.engine.currentScore() ] ) )
        return gameElements

    def applyAction( self, iPlayer, podAction ):
        assert type(podAction) == type( hacka.Pod() )
        action= podAction.label()
        # Apply the action choosen by the player iPlayer. return a boolean at True if the player terminate its actions for the current turn.
        self.score= self.engine.step( action )
        return True

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return self.engine.isEnded()

    def playerScore( self, iPlayer ):
        # return the player score for the current game (usefull at game ending)
        return self.score

class GameDuo( hacka.AbsGame ) :

    # Constructor: 
    def __init__(self):
        self._startHorizon= 3
        self._refDices= [0, 0 ,0]
        self._lastPlayer= 0

    # Accessors: 
    def numberOfPlayer(self):
        return 2
    
    def refDices(self) :
        return self._refDices

    def initialize(self):
        # Initialize a new game (not returning anything)
        self.engine= ge.Engine421()
        self.engine.initialize(self._startHorizon)
        self._refDices= [0, 0 ,0]
        self._lastPlayer= 0
        return hacka.Pod().initialize( '421-Duo' )

    def playerHand( self, iPlayer ):
        if (self._lastPlayer == 0 and iPlayer == 1) or (self._lastPlayer != 0 and iPlayer == 2) :
            return self.currentPlayerHand()
        else :
            return self.opponentPlayerHand()

    def currentPlayerHand( self ):
        # Return the game elements in the player vision (an AbsGamel)
        gameElements= hacka.Pod().initialize( '421-Duo' )
        gameElements.append( hacka.Pod().initialize( 'Horizon', [ self.engine.turn() ] ) )
        gameElements.append( hacka.Pod().initialize( 'Dices',
                                        self.engine.dices(),
                                        [ self.engine.currentScore() ] 
                                    )
                            )
        gameElements.append( hacka.Pod().initialize( 'Opponent',
                                       self.refDices(),
                                       [ self.engine.scoreDices( self.refDices() ) ]
                                    )
                            )
        return gameElements
    
    def opponentPlayerHand( self ):
        # Return the game elements in the player vision (an AbsGamel)
        gameElements= hacka.Pod().initialize( '421-Duo' )
        gameElements.append( hacka.Pod().initialize( 'Horizon', [ 0 ] ) )
        gameElements.append( hacka.Pod().initialize( 'Dices',
                                       self.refDices(),
                                       [ self.engine.scoreDices( self.refDices() ) ]
                                    )
                            )
        gameElements.append( hacka.Pod().initialize( 'Opponent',
                                        self.engine.dices(),
                                        [ self.engine.currentScore() ] 
                                    )
                            )
        return gameElements
    
    def applyAction( self, iPlayer, podAction ):
        assert type(podAction) == type( hacka.Pod() )
        action= podAction.label()
        # Apply the action choosen by the player iPlayer. return a boolean at True if the player terminate its actions for the current turn.
        self.engine.step( action )
        if iPlayer == 1 and self.engine.isEnded() :
            self._refDices= [ d for d in self.engine.dices() ]
            self.engine.initialize( self._startHorizon-self.engine.turn() )
            self._lastPlayer= 1
            return True
        elif self.engine.isEnded() :
            self._lastPlayer= 2
            return True
        return False

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return self._lastPlayer == 2 and self.engine.isEnded()

    def playerScore( self, iPlayer ):
        # Get appropriate combinaison:
        if iPlayer == 1: 
            ipCombi= self.refDices()
            opCombi= self.engine.dices()
        else :
            ipCombi= self.engine.dices()
            opCombi= self.refDices()
        
        # Compute scores:
        ipScore= self.engine.score( { "D1": ipCombi[0], "D2": ipCombi[1], "D3": ipCombi[2] } )
        opScore= self.engine.score( { "D1": opCombi[0], "D2": opCombi[1], "D3": opCombi[2] } )

        # Compare:
        if ipScore > opScore :
            return 1
        elif ipScore < opScore :
            return -1
        else :
            return 0

class GameMaster( hacka.SequentialGameMaster ):
    def __init__( self, mode= "Solo" ):
        if mode == "Solo" :
            game= GameSolo()
        elif mode == "Duo" :
            game= GameDuo()
        else :
            warnings.warn('Py421::GameMaster: Unrecognized mode, should be "Solo" or "Duo"')
            game= GameSolo()
        super().__init__( game, game.numberOfPlayer() )

def command():
    from hacka.command import Command, Option

    cmd= Command( "play",
    [
        Option( "port", "p", default=1400 ),
        Option( "number", "n", 1, "number of games" )
    ],
    "Play to hackagames py421. ARGUMENTS can be: Solo or Duo" )

    # Process the command line: 
    cmd.process()
    if not cmd.ready() :
        print( cmd.help() )
        return False
    return cmd

def play():
    from hacka.player import PlayerShell
    from .firstBot import Bot as Opponent

    # Process the command line: 
    cmd= command()
    if not cmd :
        exit()

    # Start the player the command line: 
    if cmd.argument() in [ "Duo", "duo" ] :
        gameMaster= GameMaster("Duo")
        gameMaster.launchLocal(  [PlayerShell(), Opponent()], cmd.option("number") )  
    else :
        gameMaster= GameMaster("Solo")
        gameMaster.launchLocal(  [PlayerShell()], cmd.option("number") )  

def launch():
    # Process the command line: 
    cmd= command()
    if not cmd :
        exit()

   # Start the player the command line: 
    mode= "Solo"
    if cmd.argument() in [ "Duo", "duo" ] :
        mode= "Duo"
    
    gameMaster= GameMaster(mode)
    gameMaster.launchOnNet( cmd.option("number"), cmd.option("port") )
