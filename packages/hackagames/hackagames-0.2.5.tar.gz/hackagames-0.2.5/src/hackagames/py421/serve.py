"""
HackaGame - Game - 421 
"""
from ...py.command import Command, Option
from . import GameSolo, GameDuo

# script :
if __name__ == '__main__' :
    # Commands:
    cmd= Command(
            "start-server",
            [
                Option( "port", "p", default=1400 ),
                Option( "number", "n", 2, "number of games" )
            ],
            (
                "star a server fo gamePy421 on your machine. "
                "ARGUMENTS refers to game mode: solo or duo."
            ))

    cmd.process()
    if cmd.ready() :
        if cmd.argument() == "duo" :
            game= GameDuo()
        else :
            game= GameSolo()
    else :
        print( cmd.help() )
        exit()

    # start:
    game.start( cmd.option("number"), cmd.option("port") )
