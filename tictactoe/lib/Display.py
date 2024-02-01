import os

from lib.Board import Board

class Display:
    def game(player: str, board: Board) -> None:
        os.system('cls')
        print(f'{player}\'s turn\n')

        board.printWithLabel() 
        
        print(f'\nWaiting for {player} to make a move...')

    def gameClient(player: str, board: Board) -> None:
        os.system('cls')
        print(f'Your turn\n')
        board.printWithLabel()
        print(f'\nChoose a cell:', end=' ') 

    def waitForOpponent(board: Board) -> None:
        os.system('cls')
        print(f"Opponent's turn\n")
        board.printWithLabel()
        print(f'\nWaiting for opponent...')

    def gameResult(state, player1: str, player2: str, board: Board) -> None:
        os.system('cls')
        print('GAME FINISHED\n')
        board.print()
        if state == 4:
            print(f'\n{player1} wins!')
        elif state == 5:
            print(f'\n{player2} wins!')
        else:
            print('\n Game tie!')

    def gameResultClient(state, board: Board) -> None:
        os.system('cls')
        if state == 4:
            print('CONGRATULATIONS!\n')
            board.print()
            print(f'\nYou win the game!')
        elif state == 5:
            print('BETTER LUCK NEXT TIME!\n')
            board.print()
            print(f'\nYou lose!')
        else:
            print('BALANCED!\n')
            board.print()
            print('\n Game tie!')

    def errorExit() -> None:
        os.system('cls')
        print('AN ERROR OCCURED')

        print('\nStopping the game successful')



        