from ...py.player import PlayerIHM

# Script
def main() :
    player= Interface()
    player.takeASeat()

class Interface( PlayerIHM ) :
    pass

# Script :
if __name__ == '__main__' :
    main()
