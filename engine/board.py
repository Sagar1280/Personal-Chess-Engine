
import numpy as np

class Board:
    def __init__(self):
        self.board = [[0 for _ in range(8)] for _ in range(8)] #create an 8x8 board filled with zeros
        self.side_to_move = 1 #1 for white, -1 for black

        self.castling_rights = {
            'white_kingside' : True,
            'white_queenside' : True,   
            'black_kingside' : True,
            'black_queenside' : True
        }

        self.halfmove_clock = 0
        self.move_number = 1
        self.en_passant = None
        self.move_history = []

    def set_up_initial_position(self): 

        self.board[0] = [-4, -2, -3, -5, -6, -3, -2, -4]
        self.board[1] = [-1 for _ in range(8)]
        self.board[6] = [1 for _ in range(8)]
        self.board[7] = [4, 2, 3, 5, 6, 3, 2, 4]   
        
        for i in range(2,6):
            self.board[i] = [0 for _ in range(8)] 
        
    def print_board(self):
        piece_markings = {
            0 : '.', 
            1 : 'P', -1 : 'p',
            2 : 'N', -2 : 'n',
            3 : 'B', -3 : 'b',
            4 : 'R', -4 : 'r',
            5 : 'Q', -5 : 'q',
            6 : 'K', -6 : 'k'
        }
        for row in self.board:
            print(' '.join(piece_markings[piece] for piece in row))
        print("\n")
        print(f"side to move: {'White' if self.side_to_move == 1 else 'Black'}")

    def load_board(self, fen):

        parts = fen.split()
        rows = parts[0].split("/")
        for r in range(8):
            file = 0
            for char in rows[r]:
               if char.isdigit():
                   file += int(char)
               else:
                piece_map = {
                    "P": 1, "N": 2, "B": 3, "R": 4, "Q": 5, "K": 6,
                    "p": -1, "n": -2, "b": -3, "r": -4, "q": -5, "k": -6
                }
                self.board[r][file] = piece_map[char]
                file += 1

        self.side_to_move = 1 if parts[1] == 'w' else -1

        self.castling_rights = {
            'white_kingside' : 'K' in parts[2],
            'white_queenside' : 'Q' in parts[2],   
            'black_kingside' : 'k' in parts[2],
            'black_queenside' : 'q' in parts[2]
        }

        if parts[3] != "-":
            file = ord(parts[3][0]) - ord('a')
            rank = 8 - int(parts[3][1])
            self.en_passant = (rank, file)
        else:
            self.en_passant = None

        self.halfmove_clock = int(parts[4])

        self.move = int(parts[5])

    def make_move(self,move):
        #Store the move and the pieces involed for undoing later
        piece = self.board[move.start_row][move.start_column]
        captured_piece = self.board[move.end_row][move.end_column]

        #saving move for undoing later
        self.move_history.append((move, piece, captured_piece, self.castling_rights.copy(), self.en_passant, self.halfmove_clock, self.move_number))

        #Making the Move
        self.board[move.end_row][move.end_column] = piece
        self.board[move.start_row][move.start_column] = 0
        
        #Changing the side to move
        self.side_to_move *= -1
        
        #no draw rule and move number handling
        if piece == 1 or piece == -1 or captured_piece != 0:
            self.halfmove_clock = 0
        else: 
            self.halfmove_clock += 1
        
        #updating move  numnber
        if self.side_to_move == 1:
            self.move_number += 1
    
    def undo_move(self):
        if not self.move_history:
            return
        
        move, piece, captured_piece, castling_rights, en_passant, halfmove_clock, move_number = self.move_history.pop()

        #undo the move
        self.board[move.start_row][move.start_column] = piece
        self.board[move.end_row][move.end_column] = captured_piece

        #restore the state
        self.castling_rights = castling_rights
        self.en_passant = en_passant
        self.halfmove_clock = halfmove_clock
        self.move_number = move_number

        #change the side to move back
        self.side_to_move *= -1