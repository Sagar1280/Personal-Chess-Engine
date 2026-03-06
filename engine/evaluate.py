class Evaluator:
    def __init__(self):
        self.piece_values = {
            1 : 100 ,
            2 : 320 ,
            3 : 330 ,
            4 : 500 ,
            5 : 900 ,
            6 : 20000
        }

        self.pawn_table = [
        [ 0,  0,  0,  0,  0,  0,  0,  0],   # 8th rank (promotion handled separately)
        [50, 50, 50, 50, 50, 50, 50, 50],   # 7th rank (very strong)
        [20, 25, 30, 35, 35, 30, 25, 20],   # 6th rank
        [10, 15, 20, 25, 25, 20, 15, 10],   # 5th rank
        [ 5, 10, 15, 20, 20, 15, 10,  5],   # 4th rank
        [ 0,  5, 10, 15, 15, 10,  5,  0],   # 3rd rank
        [ 5,  5,  5, -5, -5,  5,  5,  5],   # 2nd rank (discourage blocking center)
        [ 0,  0,  0,  0,  0,  0,  0,  0]    # 1st rank
        ]

        
        self.knight_table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],  # 8
            [-40, -20,   0,   5,   5,   0, -20, -40],  # 7
            [-30,   5,  15,  20,  20,  15,   5, -30],  # 6
            [-30,  10,  20,  30,  30,  20,  10, -30],  # 5
            [-30,  10,  20,  30,  30,  20,  10, -30],  # 4
            [-30,   5,  15,  20,  20,  15,   5, -30],  # 3
            [-40, -20,   0,   5,   5,   0, -20, -40],  # 2
            [-50, -40, -30, -30, -30, -30, -40, -50]   # 1
        ]

        self.bishop_table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],  
            [-10,   5,   0,   0,   0,   0,   5, -10],  
            [-10,  10,  10,  15,  15,  10,  10, -10],  
            [-10,   0,  15,  20,  20,  15,   0, -10], 
            [-10,   5,  15,  20,  20,  15,   5, -10],  
            [-10,   5,   0,   0,   0,   0,   5, -10], 
            [-10,   0,   0,   0,   0,   0,   0, -10], 
            [-20, -10, -10, -10, -10, -10, -10, -20] 
        ] 

        self.rook_table = [
            [  0,   0,   5,  10,  10,   5,   0,   0],  
            [ 20,  20, 20,  20,  20,  20,  20,  20 ],  
            [ -5,   0,   5,  10,  10,   5,   0,  -5],  
            [ -5,   0,   5,  10,  10,   5,   0,  -5],  
            [ -5,   0,   5,  10,  10,   5,   0,  -5],  
            [ -5,   0,   5,  10,  10,   5,   0,  -5],   
            [ -5,   0,   0,   5,   5,   0,   0,  -5],   
            [  0,   0,   5,  10,  10,   5,   0,   0]     
        ]

        self.queen_table = [
            [-20, -10, -10,  -5,  -5, -10, -10, -20],  
            [-10,   0,   0,   0,   0,   0,   0, -10],  
            [-10,   0,   5,   5,   5,   5,   0, -10],  
            [ -5,   0,   5,   5,   5,   5,   0,  -5],  
            [ -5,   0,   5,   5,   5,   5,   0,  -5],    
            [-10,   0,   5,   5,   5,   5,   0, -10],   
            [-10,   0,   0,   0,   0,   0,   0, -10],   
            [-20, -10, -10 , -5 , -5 , -10,-10 ,-20]    
        ]

        self.king_middle_table = [
            [-50,-40,-40,-40,-40,-40,-40,-50],
            [-30,-30,-30,-30,-30,-30,-30,-30],
            [-20,-20,-20,-20,-20,-20,-20,-20],
            [-10,-10,-10,-10,-10,-10,-10,-10],
            [0 ,0 , -10, -20, -20,-10, 0, 0 ],
            [10, 10,-5, -10, -10, -5, 10, 10],
            [20 , 20, 0 , 0 , 0 , 0, 20 , 20],
            [30,40,10 , 0 , 0 , 10 , 40 , 30]
        ]

        self.king_end_table = [
            [-50, -30, -20, -10, -10, -20, -30, -50],
            [-30, -10,   0,   5,   5,   0, -10, -30],
            [-20,   0,  10,  15,  15,  10,   0, -20],
            [-10,   5,  15,  20,  20,  15,   5, -10],
            [-10,   5,  15,  20,  20,  15,   5, -10],
            [-20,   0,  10,  15,  15,  10,   0, -20],
            [-30, -10,   0,   5,   5,   0, -10, -30],
            [-50 , -30, -20,-10, -10, -20, -30, -50]
        ]

    def is_endgame(self,board):
        total_material =0

        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]
                if piece != 0 and abs(piece) != 6:  # Exclude kings from material count
                    total_material += self.piece_values[abs(piece)]

        return total_material < 1500  # Threshold for endgame
        
    def evaluate(self,board):
        score = 0
        endgame = self.is_endgame(board)
        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]

                if piece == 0:
                    continue

                abs_piece = abs(piece)
                value = self.piece_values[abs_piece]

                if piece > 0:
                    score += value
                else:
                    score -= value 

                if abs_piece == 1:  # Pawn
                    if piece > 0:
                        score += self.pawn_table[r][c]
                    else:
                        score -= self.pawn_table[7-r][c]

                elif abs_piece == 2:  # Knight
                    if piece > 0:
                        score += self.knight_table[r][c]
                    else:
                        score -= self.knight_table[7-r][c]

                elif abs_piece == 3:  # Bishop  
                    if piece > 0:
                        score += self.bishop_table[r][c]
                    else:
                        score -= self.bishop_table[7-r][c]

                elif abs_piece == 4:  # Rook
                    if piece > 0:
                        score += self.rook_table[r][c]
                    else:
                        score -= self.rook_table[7-r][c]

                elif abs_piece == 5:  # Queen
                    if piece > 0:
                        score += self.queen_table[r][c]
                    else:
                        score -= self.queen_table[7-r][c]

                elif abs_piece == 6:  # King
                    #add bonus to castling before move 15
                    if piece > 0:
                        if board.board[7][6] == 6 or board.board[7][2] == 6:
                            if board.move_number < 15:
                                score += 50
                            if board.board[7][4] == 6 and board.move_number > 12:
                                score += -25
                    else:
                        if board.board[0][6] == -6 or board.board[0][2] == -6:
                            if board.move_number < 15:
                                score += 50
                            if board.board[0][4] == -6 and board.move_number > 12:
                                score += -25
                
                    
                    if piece > 0:
                        if board.castling_rights["white_kingside"] == False and board.castling_rights["white_queenside"] == False:
                            score += -10
                    else:
                        if board.castling_rights["white_kingside"] == False and board.castling_rights["white_queenside"] == False:
                            score += -10
                     
                    if endgame:
                        if piece > 0:
                            score += self.king_end_table[r][c]
                        else:
                            score -= self.king_end_table[7-r][c]
                    else:
                        if piece > 0:
                            score += self.king_middle_table[r][c]
                        else:
                            score -= self.king_middle_table[7-r][c] 
        
        if board.side_to_move == -1:
            score = -score
        
        return score
    
