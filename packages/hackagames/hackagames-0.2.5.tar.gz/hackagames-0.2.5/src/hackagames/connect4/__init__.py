"""
HackaGame - Game - Connect4 
"""
import sys, random

sys.path.insert(1, __file__.split('Connect4')[0])
import hacka as hk
from . import grid
from . import firstBot
from . import shell

Grid= grid.Grid

class Game( hk.AbsGame ) :
    
    # Initialization:
    def __init__(self, nbColumns=7, nbLines=6) :
        self._nbColumns= nbColumns
        self._nbLines= nbLines
    
    # Game interface :
    def initialize(self):
        self._grid= Grid( self._nbColumns, self._nbLines )
        return hk.Pod().initialize( 'Connect4', [ self._nbColumns, self._nbLines ] )
        
    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (an AbsGamel)
        return self._grid.asPod()

    def applyAction( self, iPlayer, podAction ):
        assert type(podAction) == type( hk.Pod() )
        action= podAction.label()
        options= self._grid.possibilities()
        if not action in options :
            action= random.choice( options )
        self._grid.playerPlay( iPlayer, action )
        return True

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return (self._grid.possibilities() == [] or self._grid.winner() != 0)
    
    def playerScore( self, iPlayer ):
        if self._grid.winner() == iPlayer :
            return 1
        elif self._grid.winner() == 0 :
            return 0
        return -1

class Connect4Master( hk.SequentialGameMaster ) :
    def __init__(self, nbColumns=7, nbLines=6) :
        super().__init__( Game(nbColumns, nbLines), 2 )

def command():
    from hacka.command import Command, Option

    cmd= Command( "play",
    [
        Option( "port", "p", default=1400 ),
        Option( "number", "n", 1, "number of games" )
    ],
    "Start interactive Game. Game do not take ARGUMENT." )

    # Process the command line: 
    cmd.process()
    if not cmd.ready() :
        print( cmd.help() )
        return False
    return cmd

def play():
    from .shell import PlayerShell
    from .firstBot import Bot
    
    # Process the command line: 
    cmd= command()
    if not cmd :
        exit()
    
    gameMaster= Connect4Master()
    gameMaster.launchLocal(  [PlayerShell(), Bot()], cmd.option("number") )  

def launch():
    # Process the command line: 
    cmd= command()
    if not cmd :
        exit()
    gameMaster= Connect4Master()
    gameMaster.launchOnNet( cmd.option("number"), cmd.option("port") )

def connect():
    assert False == "To do..."
