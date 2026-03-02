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
    
    def evaluate(self,board):
        score = 0
        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]

                if piece != 0:
                    value = self.piece_values[abs(piece)]
                    score += value if piece > 0 else -value
        return score