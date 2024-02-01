import sys

from lib.GameClient import GameClient

if __name__ == "__main__":
    # Argument validation
    if len(sys.argv) != 3:
        print("Usage: python client.py <client port> <server port>")
        sys.exit(1)
    client_port = int(sys.argv[1])
    server_port = int(sys.argv[2])

    # Start the main app
    game = GameClient()
    game.start(client_port, server_port)