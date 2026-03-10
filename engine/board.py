
from email import generator
from engine.zobrist import Zobrist

import numpy as np

from engine.move_generator import MoveGenerator

class Board:
    def __init__(self):
        
        self.board = [[0 for _ in range(8)] for _ in range(8)] #create an 8x8 board filled with .
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

        self.zobrist = Zobrist()
        self.hash = 0;

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
        parts = fen.strip().split()
        if len(parts) < 2:
            raise ValueError("Invalid FEN: need at least piece placement and side to move")

        # Always clear the board first
        for i in range(8):
            for j in range(8):
                self.board[i][j] = 0

        piece_map = {
            "P": 1, "N": 2, "B": 3, "R": 4, "Q": 5, "K": 6,
            "p": -1, "n": -2, "b": -3, "r": -4, "q": -5, "k": -6
        }

        rows = parts[0].split("/")
        for r in range(8):
            file = 0
            for char in rows[r]:
                if char.isdigit():
                    file += int(char)
                elif char in piece_map:
                    self.board[r][file] = piece_map[char]
                    file += 1

        self.side_to_move = 1 if parts[1] == 'w' else -1

        castling = parts[2] if len(parts) > 2 else "-"
        self.castling_rights = {
            'white_kingside':  'K' in castling,
            'white_queenside': 'Q' in castling,
            'black_kingside':  'k' in castling,
            'black_queenside': 'q' in castling,
        }

        ep = parts[3] if len(parts) > 3 else "-"
        if ep != "-":
            self.en_passant = (8 - int(ep[1]), ord(ep[0]) - ord('a'))
        else:
            self.en_passant = None

        self.halfmove_clock = int(parts[4]) if len(parts) > 4 else 0
        self.move_number    = int(parts[5]) if len(parts) > 5 else 1
        self.hash = self.compute_hash()

    def make_move(self, move):  
      # Store move info for undo
        piece = self.board[move.start_row][move.start_column]
        captured_piece = self.board[move.end_row][move.end_column]

        # Detect castling NOW, before castling_rights are modified below
        is_wk_castle = (piece == 6  and move.start_row == 7 and move.start_column == 4 and move.end_row == 7 and move.end_column == 6 and self.castling_rights.get('white_kingside',  False))
        is_wq_castle = (piece == 6  and move.start_row == 7 and move.start_column == 4 and move.end_row == 7 and move.end_column == 2 and self.castling_rights.get('white_queenside', False))
        is_bk_castle = (piece == -6 and move.start_row == 0 and move.start_column == 4 and move.end_row == 0 and move.end_column == 6 and self.castling_rights.get('black_kingside',  False))
        is_bq_castle = (piece == -6 and move.start_row == 0 and move.start_column == 4 and move.end_row == 0 and move.end_column == 2 and self.castling_rights.get('black_queenside', False))

        self.move_history.append((
            move, piece, captured_piece,
            self.castling_rights.copy(),
            self.en_passant,
            self.halfmove_clock,
            self.move_number,
            self.hash
        ))

        # Toggle side to move in hash
        self.hash ^= self.zobrist.side_key

        # Remove moving piece from start square
        piece_index = (abs(piece) - 1) + (0 if piece > 0 else 6)
        start_square = move.start_row * 8 + move.start_column
        self.hash ^= self.zobrist.piece_keys[piece_index][start_square]

        # Remove captured piece
        if captured_piece != 0:
            captured_index = (abs(captured_piece) - 1) + (0 if captured_piece > 0 else 6)
            end_square = move.end_row * 8 + move.end_column
            self.hash ^= self.zobrist.piece_keys[captured_index][end_square]

        # Add moving piece to end square
        end_square = move.end_row * 8 + move.end_column
        self.hash ^= self.zobrist.piece_keys[piece_index][end_square]

        # Make the move
        self.board[move.end_row][move.end_column] = piece
        self.board[move.start_row][move.start_column] = 0

        #   KING MOVED → remove castling rights
        if abs(piece) == 6:
            if piece > 0:
                self.remove_castling_right("white_kingside")
                self.remove_castling_right("white_queenside")
            else:
                self.remove_castling_right("black_kingside")
                self.remove_castling_right("black_queenside")

        # ROOK MOVED → remove corresponding castling
        if abs(piece) == 4:
            if piece > 0 and move.start_row == 7 and move.start_column == 7:
                self.remove_castling_right("white_kingside")

            if piece > 0 and move.start_row == 7 and move.start_column == 0:
                self.remove_castling_right("white_queenside")

            if piece < 0 and move.start_row == 0 and move.start_column == 7:
                self.remove_castling_right("black_kingside")

            if piece < 0 and move.start_row == 0 and move.start_column == 0:
                self.remove_castling_right("black_queenside")

        # ROOK CAPTURED → remove castling rights
        if captured_piece == 4:
            if move.end_row == 7 and move.end_column == 0:
                self.remove_castling_right("white_queenside")

            if move.end_row == 7 and move.end_column == 7:
                self.remove_castling_right("white_kingside")

        if captured_piece == -4:
            if move.end_row == 0 and move.end_column == 0:
                self.remove_castling_right("black_queenside")

            if move.end_row == 0 and move.end_column == 7:
                self.remove_castling_right("black_kingside")

        # CASTLING MOVE → move rook (use pre-computed flags from top of function)
        if is_wk_castle:
            self.board[7][5] = self.board[7][7]
            self.board[7][7] = 0

        if is_wq_castle:
            self.board[7][3] = self.board[7][0]
            self.board[7][0] = 0

        if is_bk_castle:
            self.board[0][5] = self.board[0][7]
            self.board[0][7] = 0

        if is_bq_castle:
            self.board[0][3] = self.board[0][0]
            self.board[0][0] = 0

         # Change side to move
        self.side_to_move *= -1

        # 50 move rule
        if abs(piece) == 1 or captured_piece != 0:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Move number update
        if self.side_to_move == 1:
            self.move_number += 1
    
    def remove_castling_right(self,right):
        if self.castling_rights[right]:
            self.hash ^= self.zobrist.castling_keys[right]
            self.castling_rights[right]= False

    
    def undo_move(self):
        if not self.move_history:
            return
        
        (move,piece,captured_piece,
        castling_rights, en_passant,
        halfmove_clock, move_number,
        previous_hash) = self.move_history.pop()

        #undo the move
        self.board[move.start_row][move.start_column] = piece
        self.board[move.end_row][move.end_column] = captured_piece

        #undo castling
        if abs(piece) == 6 and abs(move.start_column - move.end_column) == 2:

            row = move.start_row

            if move.end_column == 6:
                self.board[row][7] = self.board[row][5]
                self.board[row][5] = 0
            elif move.end_column == 2:
                self.board[row][0] = self.board[row][3]
                self.board[row][3] = 0


        #restore the state
        self.castling_rights = castling_rights
        self.en_passant = en_passant
        self.halfmove_clock = halfmove_clock
        self.move_number = move_number
        self.hash = previous_hash

        #change the side to move back
        self.side_to_move *= -1

    def find_king(self,color):

        king_value = 6 * color
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king_value:
                    return (r,c)
        return None
    
    def is_in_check(self,color):
        king_pos = self.find_king(color)
        
        if not king_pos:
            return False

        king_r, king_c = king_pos

        # Temporarily switch side to generate opponent moves
        original_side = self.side_to_move
        self.side_to_move = -color

        from engine.move_generator import MoveGenerator
        generator = MoveGenerator(self)
        opponent_moves = generator.generate_moves(include_castling = False)

        self.side_to_move = original_side

        for move in opponent_moves:
            if move.end_row == king_r and move.end_column == king_c:
                return True

        return False
    
    def compute_hash(self): 
        h = 0

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != 0:
                 piece_index = (abs(piece) - 1) + (0 if piece > 0 else 6)
                 square = r * 8 + c
                 h ^= self.zobrist.piece_keys[piece_index][square]

        if self.side_to_move == -1:
            h ^= self.zobrist.side_key

        for key, value in self.castling_rights.items():
            if value:
             h ^= self.zobrist.castling_keys[key]

        if self.en_passant:
            file = self.en_passant[1]
            h ^= self.zobrist.en_passant_keys[file]

        return h
    
    def is_checkmate(self):
        if not self.is_in_check(self.side_to_move):
            return False
        
        generator = MoveGenerator(self)
        legal_moves = generator.generate_legal_moves()

        return len(legal_moves) == 0
    
    def is_stalemate(self):
        if self.is_in_check(self.side_to_move):
            return False
        
        generator = MoveGenerator(self)
        legal_moves = generator.generate_legal_moves()

        return len(legal_moves) == 0
    
    def is_check(self):
        return self.is_in_check(self.side_to_move)
    
    def get_fenn(self): 

        fen = ""
        for r in range(8):
            empty_count = 0
            for c in range(8):
                piece = self.board[r][c]
                if piece == 0:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += str(empty_count)
                        empty_count = 0
                    piece_map = {
                        1 : 'P', -1 : 'p',
                        2 : 'N', -2 : 'n',
                        3 : 'B', -3 : 'b',
                        4 : 'R', -4 : 'r',
                        5 : 'Q', -5 : 'q',
                        6 : 'K', -6 : 'k'
                    }
                    fen += piece_map[piece]
            if empty_count > 0:
                fen += str(empty_count)
            if r < 7:
                fen += "/"

        fen += " " + ("w" if self.side_to_move == 1 else "b") #w / b

        castling = ""
        if self.castling_rights['white_kingside']:
            castling += "K"
        if self.castling_rights['white_queenside']:
            castling += "Q"
        if self.castling_rights['black_kingside']:
            castling += "k"
        if self.castling_rights['black_queenside']:
            castling += "q"
        fen += " " + (castling if castling else "-")

        if self.en_passant:
            file = chr(self.en_passant[1] + ord('a'))
            rank = str(8 - self.en_passant[0])
            fen += f" {file}{rank}"
        else:
            fen += " -"

        fen += f" {self.halfmove_clock} {self.move_number}"

        return fen