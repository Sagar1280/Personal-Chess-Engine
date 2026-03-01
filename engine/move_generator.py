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
        return moves

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
    