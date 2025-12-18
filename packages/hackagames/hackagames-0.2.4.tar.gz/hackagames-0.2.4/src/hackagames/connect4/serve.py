"""
HackaGame - Game - Hello 
"""
from . import Game
from hacka.command import Command, Option

# script :
if __name__ == '__main__' :
    # Define a command interpreter: 2 options: host address and port:
    cmd= Command(
            "start-server",
            [
                Option( "port", "p", default=1400 ),
                Option( "number", "n", 2, "number of games" )
            ],
            (
                "star a server fo Connect4 on your machine. "
                "Connect4 do not take ARGUMENT."
            ))
    # Process the command line: 
    cmd.process()
    if not cmd.ready() :
        print( cmd.help() )
        exit()

    # Start the player the command line: 
    game= Game()

    game.start( cmd.option("number"), cmd.option("port") )
