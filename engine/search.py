class Search:
    def __init__(self, board, generator, evaluator):
        self.board = board
        self.generator = generator
        self.evaluator = evaluator
        self.tt = {}
        self.tt_hits = 0

        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
    
    def quiescence(self, alpha, beta) -> float:
        stand_pat = self.evaluator.evaluate(self.board)

        # Alpha-beta bounding
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Only explore captures
        captures = self.generator.generate_capture_moves()

        # Order captures (good captures first)
        for move in captures:
            move.score = self.score_move(move)

        captures.sort(key=lambda m: m.score, reverse=True)

        for move in captures:
            self.board.make_move(move)
            score = -self.quiescence(-beta, -alpha)
            self.board.undo_move()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def score_move(self, move):
        target_piece = self.board.board[move.end_row][move.end_column]
        moving_piece = self.board.board[move.start_row][move.start_column]

        if target_piece != 0:
            return 10000 + 10 * abs(target_piece) - abs(moving_piece)
        
        self.board.make_move(move)
        if self.board.is_in_check(-self.board.side_to_move):
            self.board.undo_move()
            return 50
        self.board.undo_move()

        return 0

    def alphabeta(self, depth, alpha, beta, maximizing_player) -> float:
        alpha_original = alpha
        beta_original = beta    

        #TRANSPOSITION TABLE LOOKUP
        if self.board.hash in self.tt:
            entry = self.tt[self.board.hash]
            if entry["depth"] >= depth:
                self.tt_hits += 1
                if entry["flag"] == self.Exact:
                    return entry["value"]
                
                elif entry["flag"] == self.LowerBound:
                    alpha = max(alpha, entry["value"])

                elif entry["flag"] == self.UpperBound:
                    beta = min(beta, entry["value"])
                if alpha >= beta:
                    return entry["value"]
           
        if depth == 0:
            return self.evaluator.evaluate(self.board)

        moves = self.generator.generate_legal_moves()

        # Checkmate / stalemate
        if not moves:
            if self.board.is_in_check(self.board.side_to_move):
                if maximizing_player:
                    return float('-inf')  # Checkmate for maximizing player
                else:        
                   return float('inf')   # Checkmate for minimizing player  
            else:
                return 0  # Stalemate

        # ORDER MOVES BEFORE SEARCH
        for move in moves:
            move.score = self.score_move(move)

        moves.sort(key=lambda m: m.score, reverse=True)

        if maximizing_player:
            value = float('-inf')

            for move in moves:
                self.board.make_move(move)
                child_value = self.alphabeta(depth - 1, alpha, beta, False)
                self.board.undo_move()

                value = max(value, child_value)
                alpha = max(alpha, value)

                if beta <= alpha:
                    break  # pruning

        else:
            value = float('inf')

            for move in moves:
                self.board.make_move(move)
                child_value = self.alphabeta(depth - 1, alpha, beta, True)
                self.board.undo_move()


                value = min(value, child_value)
                beta = min(beta, value)

                if beta <= alpha:
                    break  # pruning

        # TRANSPOSITION TABLE STORE
        if value <= alpha_original:
            flag = self.UpperBound  
        elif value >= beta:
            flag = self.LowerBound
        else:
            flag = self.Exact

        self.tt[self.board.hash] = {
                "value": value, 
                "depth": depth,
                "flag" : flag,
                }
        return value

    def find_best_move(self, depth):

        best_move = None
        maximizing_player = self.board.side_to_move == 1

        if maximizing_player:
          best_eval = float('-inf')
        else:
          best_eval = float('inf')

        alpha = float('-inf')
        beta = float('inf')

        moves = self.generator.generate_legal_moves()

        # Order root moves too
        for move in moves:
            move.score = self.score_move(move)

        moves.sort(key=lambda m: m.score, reverse=True)

        for move in moves:
            self.board.make_move(move)
            eval_score = self.alphabeta(depth - 1, alpha, beta, not maximizing_player)
            self.board.undo_move()



            if maximizing_player:
                if eval_score > best_eval:
                   best_eval = eval_score
                   best_move = move
                alpha = max(alpha, eval_score)
            else:
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)

        return best_move, best_eval