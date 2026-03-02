from engine.move import Move

class MoveGenerator:
    def __init__(self, board):
        self.board = board

    def generate_moves(self):
        moves = []

        for r in range(8):
            for c in range(8):
                piece = self.board.board[r][c]

                if piece == 0:
                    continue

                if piece * self.board.side_to_move > 0:
                    if abs(piece) == 1:
                        moves.extend(self.generate_pawn_moves(r, c))
                    elif abs(piece) == 2:
                        moves.extend(self.generate_knight_moves(r, c))
                    elif abs(piece) == 3:
                        moves.extend(self.generate_bishop_moves(r, c))
                    elif abs(piece) == 4:
                        moves.extend(self.generate_rook_moves(r, c))    
                    elif abs(piece) == 5:
                        moves.extend(self.generate_queen_moves(r, c))
                    elif abs(piece) == 6:
                        moves.extend(self.generate_king_moves(r, c))
                        moves.extend(self.generate_castling_moves(r, c))
        return moves
    
    def generate_legal_moves(self):
        legal_moves = []
        for move in self.generate_moves():
            self.board.make_move(move) # make the move on the board
            if not self.board.is_in_check(-self.board.side_to_move): #check if the move leavess the king in check 
                legal_moves.append(move)
            self.board.undo_move() # undo the move to restore the original position
        return legal_moves
    
    def generate_pawn_moves(self, r, c):
        moves = []
        piece = self.board.board[r][c]
        direction = -1 if piece > 0 else 1

        # Forward 1
        if 0 <= r + direction < 8:
            if self.board.board[r + direction][c] == 0:
                moves.append(Move(r, c, r + direction, c))
                # Forward 2
                if (piece > 0 and r == 6) or (piece < 0 and r == 1):
                    if self.board.board[r + 2 * direction][c] == 0:
                        moves.append(Move(r, c, r + 2 * direction, c))
        # Captures
        for dc in [-1, 1]:
            if 0 <= c + dc < 8 and 0 <= r + direction < 8:
                target_piece = self.board.board[r + direction][c + dc]
                if target_piece * self.board.side_to_move < 0:
                    moves.append(Move(r, c, r + direction, c + dc))

        return moves
    
    def generate_knight_moves(self, r, c):
        moves = []
        piece = self.board.board[r][c]
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for dr, dc in knight_moves:
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                target_piece = self.board.board[new_r][new_c]
                if target_piece == 0 or target_piece * self.board.side_to_move < 0: 
                    moves.append(Move(r, c, new_r, new_c))
        return moves
    
    def generate_slide_moves(self,r,c,directions):
        moves = []
        piece = self.board.board[r][c]
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            while 0 <= new_r < 8 and 0 <= new_c < 8:
                target_piece = self.board.board[new_r][new_c]
                if target_piece == 0:
                    moves.append(Move(r, c, new_r, new_c))
                elif target_piece * self.board.side_to_move < 0:
                    moves.append(Move(r, c, new_r, new_c))
                    break # only one capture allowed
                else:
                    break # Own piece blocking
                new_r += dr
                new_c += dc 
        return moves

    def generate_bishop_moves(self, r, c):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        moves = self.generate_slide_moves(r, c, directions)
        return moves
    
    def generate_rook_moves(self, r, c):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        moves = self.generate_slide_moves(r, c, directions)
        return moves
    
    def generate_queen_moves(self, r, c):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        moves = self.generate_slide_moves(r, c, directions)
        return moves
    
    def generate_king_moves(self, r, c):
        moves = []
        piece = self.board.board[r][c]
        king_moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dr, dc in king_moves:
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                target_piece = self.board.board[new_r][new_c]
                if target_piece == 0 or target_piece * self.board.side_to_move < 0: 
                    moves.append(Move(r, c, new_r, new_c))
        return moves
    
    def generate_castling_moves(self, r, c):
        moves = []
        piece = self.board.board[r][c]

        if piece > 0: # White
            if self.board.castling_rights['white_kingside']:
                if self.board.board[7][5] == 0 and self.board.board[7][6] == 0:
                    moves.append(Move(r, c, 7, 6)) # O-O
            if self.board.castling_rights['white_queenside']:
                if self.board.board[7][1] == 0 and self.board.board[7][2] == 0 and self.board.board[7][3] == 0:
                    moves.append(Move(r, c, 7, 2)) # O-O-O
        else: # Black
            if self.board.castling_rights['black_kingside']:
                if self.board.board[0][5] == 0 and self.board.board[0][6] == 0:
                    moves.append(Move(r, c, 0, 6)) # O-O
            if self.board.castling_rights['black_queenside']:
                if self.board.board[0][1] == 0 and self.board.board[0][2] == 0 and self.board.board[0][3] == 0:
                    moves.append(Move(r, c, 0, 2)) # O-O-O

        return moves
    

