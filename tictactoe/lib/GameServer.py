import os

from lib.Server import Server
from lib.Player import Player
from lib.Board import Board
from lib.Display import Display
from lib.Evaluator import Evaluator

class GameServer:
    # Construct the game class
    def __init__(self) -> None:
        self.server = Server()
        self.player1 = None
        self.player2 = None
        self.board = None
        self.game_status = 0 
            # 0: not started, 
            # 1: waiting for players, 
            # 2: Waiting for player 1 to make a move
            # 3: Waiting for player 2 to make a move
            # 4: Player 1 wins
            # 5: Player 2 wins
            # 6: Game tie
    
    # Start the game server
    def start_server(self, port) -> None:
        self.server.start_server(port)
    
    # Waiting for players
    def waiting_for_players(self) -> None:
        self.game_status = 1

        os.system('cls')
        print('TICTACTOE ONLINE\n')

        print('Waiting for players...')

        # Waiting for player 1
        self.server.listen_connection_request()
        self.player1 = Player(self.server.clients[0]['ip'], self.server.clients[0]['port'], 1, self.server.clients[0]['username'])
        print(f'\n{self.player1.username} joined the game!')

        # Waiting for player 2
        self.server.listen_connection_request()
        self.player2 = Player(self.server.clients[1]['ip'], self.server.clients[1]['port'], 2, self.server.clients[1]['username'])
        print(f'{self.player2.username} joined the game!')

        # Three way handshake with all the clients
        print('\nEstablishing connection...')
        self.server.perform_three_way_handshake(self.player1.ip, self.player1.port)
        self.server.perform_three_way_handshake(self.player2.ip, self.player2.port)
    
    # Setup the game
    def setup(self):
        self.board = Board()
        self.game_status = 2

    # Waiting client to make a move
    def wait_move(self):
        if self.game_status == 2:
            Display.game(self.player1.username, self.board)
            self.server.request_state(self.player1.ip, int(self.player1.port), 1, self.player1.username, self.board.board_matrix, self.game_status)
            cell = self.server.listen_move_update()
            self.board.updateBoard(cell, 1)
            self.game_status = 3
        elif self.game_status == 3:
            Display.game(self.player2.username, self.board)
            self.server.request_state(self.player2.ip, int(self.player2.port), 2, self.player2.username, self.board.board_matrix, self.game_status)
            cell = self.server.listen_move_update()
            self.board.updateBoard(cell, 2)
            self.game_status = 2
        
    # Evaluate the board
    def evaluate(self):
        evaluation = Evaluator.evaluate(self.board)
        if evaluation == 4 or evaluation == 5 or evaluation == 6:
            self.game_status = evaluation 

    # Stop the game and announce the result
    def stop_game(self):
        Display.gameResult(self.game_status, self.player1.username, self.player2.username, self.board)

        self.server.request_result(self.game_status - 3, self.board.board_matrix)

    # Start the game
    def start(self, port) -> None:
        while True:
            # Start the game server and wait for connection
            self.start_server(port)

            # Waiting for players
            self.waiting_for_players()

            # Setup the game
            self.setup()

            # Player's request and response 
            while self.game_status == 2 or self.game_status == 3:
                self.wait_move()
                self.evaluate()
            
            # Stop the game and announce the result
            self.stop_game()

            # Cleanup the state
            self.server = Server()
            self.player1 = None
            self.player2 = None
            self.board = None
            self.game_status = 0 