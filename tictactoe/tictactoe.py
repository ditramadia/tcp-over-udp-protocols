import sys

from lib.GameServer import GameServer

if __name__ == "__main__":
    # Argument validation
    if len(sys.argv) != 2:
        print("Usage: python tictactoe.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    
    # Start the main app
    game = GameServer()
    game.start(port)