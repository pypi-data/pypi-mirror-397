#!env python3
"""
HackaGames - Game - TicTacToe
"""
import hacka as hk
from . import engine
from . import firstBot
from . import shell

class Game( hk.AbsGame ):

    # Constructor
    def __init__(self, mode="classic"):
        self.mode= mode

    # Game interface :
    def initialize(self):
        if self.mode == "ultimate" :
            self.grid= engine.Ultimate()
        else :
            self.grid= engine.Classic()
        self.count= 4
        return hk.Pod().initialize( "TicTacToe-"+self.grid.name() )

    def playerHand( self, iPlayer ):
        # Return the game elements in the player vision (a POD)
        pod= self.grid.asPod()
        return pod

    def applyAction( self, iPlayer, podAction ):
        assert type(podAction) == type( hk.Pod() )
        action= podAction.label()
        # Apply the action choosen by the player iPlayer. return a boolean at True if the player terminate its actions for the current turn.
        ok= self.grid.apply( iPlayer, action )
        if ok or self.count < 1 :
            self.count= 4
            return True
        self.count-= 1
        return False

    def isEnded( self ):
        # must return True when the game end, and False the rest of the time.
        return self.grid.isEnded()

    def playerScore( self, iPlayer ):
        # If winning
        if self.grid.isWinning(iPlayer) :
            return 1
        # get openent number
        iOponent= 1
        if iPlayer == 1 :
            iOponent= 2
        # if loosing
        if self.grid.isWinning(iOponent) :
            return -1
        # else
        return 0

class TictactoeMaster( hk.SequentialGameMaster ):
    def __init__(self, mode="classic" ):
        super().__init__(Game(mode), 2)


def command():
    from hacka.command import Command, Option

    cmd= Command( "play",
    [
        Option( "port", "p", default=1400 ),
        Option( "number", "n", 1, "number of games" )
    ],
    "Start TicTacToe Game. ARGUMENTS can be: 'classic' or 'ultimate'" )

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
    
    mode= "classic"
    if cmd.argument() == "ultimate" :
        mode= "ultimate"
    
    gameMaster= TictactoeMaster(mode)
    gameMaster.launchLocal(  [PlayerShell(), Bot()], cmd.option("number") )  

def launch():
    # Process the command line: 
    cmd= command()
    if not cmd :
        exit()
    
    mode= "classic"
    if cmd.argument() == "ultimate" :
        mode= "ultimate"
    
    gameMaster= TictactoeMaster(mode)
    gameMaster.launchOnNet( cmd.option("number"), cmd.option("port") )

def connect():
    assert False == "To do..."
