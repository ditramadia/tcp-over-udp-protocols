import os

from lib.Client import Client
from lib.Board import Board
from lib.Display import Display

class GameClient:
    # Construct the game class
    def __init__(self) -> None:
        self.client = Client()
        self.id = 0
        self.you = ''
        self.board = None
        self.game_status = 0 
            # 0: not started, 
            # 1: waiting for players, 
            # 2: Waiting for you to make a move
            # 3: Waiting for opponent to make a move
            # 4: You win
            # 5: You lose
            # 6: Game tie
    
    # Start the connection with server
    def start_connection(self, client_port, server_port) -> None:
        os.system('cls')
        print('TICTACTOE ONLINE\n')
        self.you = str(input("Username: "))

        self.client.connect_to_server(client_port, server_port, self.you)

        print('\nWaiting for other players...')
        self.client.perform_three_way_handshake()

    # Setup the game
    def setup(self):
        self.board = Board()
        self.game_status = 1

    # Wait for turns
    def wait_turn(self):
        # Listen for request
        state = self.client.listen_state()

        # Determine if game is still running, or game is finished
        if state['sign'] == 'Requesting result':

            self.board.update_board_by_matrix(state['board'])

            if state['id'] == 3:
                self.game_status = 6
            elif state['id'] == self.id:
                self.game_status = 4
            elif state['id'] != self.id:
                self.game_status = 5 
            
            return 

        # Assign player id
        if self.id == 0:
            self.id = state['id']

        # Update board
        self.board.update_board_by_matrix(state['board'])

        # Ask for next move (No validation yet)
        valid = False
        while not valid:
            Display.gameClient(self.you, self.board)
            next_move = int(input())
            valid = self.board.validate(next_move)

        # Send move
        self.client.request_move_update(next_move)

        # Update board
        self.board.updateBoard(next_move, self.id)
        Display.waitForOpponent(self.board)
        
        self.game_status = 3
    
    # Stop the game
    def stop_game(self):
        Display.gameResultClient(self.game_status, self.board)

    # Start the game
    def start(self, client_port, server_port) -> None:

        # Start the game and request to connect to server
        self.start_connection(client_port, server_port)

        # Setup the game
        self.setup()

        # Wait for turns
        while self.game_status == 1 or self.game_status == 2 or self.game_status == 3:
            self.wait_turn()

        # Stop the game
        self.stop_game()

        # Stop the connection
        self.client.connection.close_socket()
        
