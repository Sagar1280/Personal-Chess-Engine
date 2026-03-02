class Search:
    def __init__(self,board,generator,evaluator):
        self.board = board
        self.generator = generator
        self.evaluator = evaluator
    
    def alphabeta(self, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.evaluator.evaluate(self.board)
        
        moves = self.generator.generate_legal_moves()

        # Checkmate / stalemate handling (important!)
        if not moves:
            if self.board.is_in_check(self.board.side_to_move):
                return -999999 if maximizing_player else 999999
            else:
                return 0  # stalemate

        if maximizing_player:
            value = float('-inf')
            for move in moves:
                self.board.make_move(move)
                value = max(value, self.alphabeta(depth - 1, alpha, beta, False))
                self.board.undo_move()

                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # 🔥 pruning
            return value
        
        else:
            value = float('inf')
            for move in moves:
                self.board.make_move(move)
                value = min(value, self.alphabeta(depth - 1, alpha, beta, True))
                self.board.undo_move()

                beta = min(beta, value)
                if beta <= alpha:
                 break  # 🔥 pruning
            return value
    
    def find_best_move(self,depth):
        best_move = None
        best_eval = float('-inf')

        alpha = float('-inf')
        beta = float('inf')

        moves = self.generator.generate_legal_moves()

        for move in moves:
            self.board.make_move(move)

            eval_score = self.alphabeta(depth - 1, alpha,beta, False)

            self.board.undo_move()

            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move   
            alpha = max(alpha, best_eval)
        return best_move, best_eval

