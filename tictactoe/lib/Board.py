class Board:
    def __init__(self) -> None:
        self.board_matrix = [[' ', ' ', ' '],
                             [' ', ' ', ' '],
                             [' ', ' ', ' ']]
        self.board_matrix_labeled = [['1', '2', '3'],
                                     ['4', '5', '6'],
                                     ['7', '8', '9']]
        #  : empty cell
        # O: player 1 mark
        # X: player 2 mark

    def updateBoard(self, cell: int, player: int) -> None:
        symbol = ''
        if player == 1:
            symbol = 'O'
        else:
            symbol = 'X'

        if (1 <= cell <= 3):
            self.board_matrix[0][cell - 1] = symbol
            return

        if (4 <= cell <= 6):
            self.board_matrix[1][cell - 4] = symbol
            return
        
        if (7 <= cell <= 9):
            self.board_matrix[2][cell - 7] = symbol
            return
    
    def update_board_by_matrix(self, matrix):
        for i in range(3):
            for j in range(3):
                self.board_matrix[i][j] = matrix[i][j]

                if matrix[i][j] != ' ':
                    self.board_matrix_labeled[i][j] = matrix[i][j]

    def print(self) -> None:
        print (f' {self.board_matrix[0][0]} | {self.board_matrix[0][1]} | {self.board_matrix[0][2]}')
        print('---+---+---')
        print (f' {self.board_matrix[1][0]} | {self.board_matrix[1][1]} | {self.board_matrix[1][2]}')
        print('---+---+---')
        print (f' {self.board_matrix[2][0]} | {self.board_matrix[2][1]} | {self.board_matrix[2][2]}')

    def printWithLabel(self) -> None:
        for i in range(3):
            for j in range(3):
                if self.board_matrix[i][j] != ' ':
                    self.board_matrix_labeled[i][j] = self.board_matrix[i][j]

        print (f' {self.board_matrix_labeled[0][0]} | {self.board_matrix_labeled[0][1]} | {self.board_matrix_labeled[0][2]}')
        print('---+---+---')
        print (f' {self.board_matrix_labeled[1][0]} | {self.board_matrix_labeled[1][1]} | {self.board_matrix_labeled[1][2]}')
        print('---+---+---')
        print (f' {self.board_matrix_labeled[2][0]} | {self.board_matrix_labeled[2][1]} | {self.board_matrix_labeled[2][2]}')

    def validate(self, cell) -> bool:
        if cell < 1 or cell > 9:
            return False

        if (1 <= cell <= 3):
            if self.board_matrix[0][cell - 1] != ' ':
                return False

        if (4 <= cell <= 6):
            if self.board_matrix[1][cell - 4] != ' ':
                return False
        
        if (7 <= cell <= 9):
            if self.board_matrix[2][cell - 7] != ' ':
                return False
        
        return True