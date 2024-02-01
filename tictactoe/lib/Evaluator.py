from lib.Board import Board

class Evaluator:
    def evaluate(board: Board) -> int:
        # Check horizontally
        if board.board_matrix[0][0] != ' ' and board.board_matrix[0][0] == board.board_matrix[0][1] == board.board_matrix[0][2]:
            if board.board_matrix[0][0] == 'O':
                return 4
            else:
                return 5
        if board.board_matrix[1][0] != ' ' and board.board_matrix[1][0] == board.board_matrix[1][1] == board.board_matrix[1][2]:
            if board.board_matrix[1][0] == 'O':
                return 4
            else:
                return 5
        if board.board_matrix[2][0] != ' ' and board.board_matrix[2][0] == board.board_matrix[2][1] == board.board_matrix[2][2]:
            if board.board_matrix[2][0] == 'O':
                return 4
            else:
                return 5
            
        # Check vertically
        if board.board_matrix[0][0] != ' ' and board.board_matrix[0][0] == board.board_matrix[1][0] == board.board_matrix[2][0]:
            if board.board_matrix[0][0] == 'O':
                return 4
            else:
                return 5
        if board.board_matrix[0][1] != ' ' and board.board_matrix[0][1] == board.board_matrix[1][1] == board.board_matrix[2][1]:
            if board.board_matrix[0][1] == 'O':
                return 4
            else:
                return 5
        if board.board_matrix[0][2] != ' ' and board.board_matrix[0][2] == board.board_matrix[1][2] == board.board_matrix[2][2]:
            if board.board_matrix[0][2] == 'O':
                return 4
            else:
                return 5
            
        # Check diagonally
        if board.board_matrix[0][0] != ' ' and board.board_matrix[0][0] == board.board_matrix[1][1] == board.board_matrix[2][2]:
            if board.board_matrix[0][0] == 'O':
                return 4
            else:
                return 5
        if board.board_matrix[0][2] != ' ' and board.board_matrix[0][2] == board.board_matrix[1][1] == board.board_matrix[2][0]:
            if board.board_matrix[0][2] == 'O':
                return 4
            else:
                return 5
        
        # Check if tie
        for i in range(3):
            for j in range(3):
                if board.board_matrix[i][j] == ' ':
                    return 0
        return 6