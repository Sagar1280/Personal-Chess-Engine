class Search:
    def __init__(self, board, generator, evaluator):
        self.board = board
        self.generator = generator
        self.evaluator = evaluator
        self.tt = {}
        self.tt_hits = 0

    def capture_moves(self):
        captures = []

        for move in self.generator.generate_legal_moves():
            target_piece = self.board.board[move.end_row][move.end_column]
            if target_piece != 0:
              captures.append(move)
        return captures
    
    def quiescence(self, alpha, beta) -> float:
        stand_pat = self.evaluator.evaluate(self.board)

        # Alpha-beta bounding
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Only explore captures
        captures = self.capture_moves()

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
            return 10 * abs(target_piece) - abs(moving_piece)

        return 0

    def alphabeta(self, depth, alpha, beta, maximizing_player) -> float:

        #TRANSPOSITION TABLE LOOKUP
        if self.board.hash in self.tt:
            entry = self.tt[self.board.hash]
            if entry["depth"] >= depth:
                self.tt_hits += 1
                return float(entry["value"])
           
        if depth == 0:
            return self.quiescence(alpha, beta)

        moves = self.generator.generate_legal_moves()

        # Checkmate / stalemate
        if not moves:
            if self.board.is_in_check(self.board.side_to_move):
                return -999999 if maximizing_player else 999999
            else:
                return 0

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

            # STORE IN TRANSPOSITION TABLE
            self.tt[self.board.hash] = {
                "value": value, 
                "depth": depth
                }

        return value

    def find_best_move(self, depth):
        best_move = None
        best_eval = float('-inf')

        alpha = float('-inf')
        beta = float('inf')

        moves = self.generator.generate_legal_moves()

        # Order root moves too
        for move in moves:
            move.score = self.score_move(move)

        moves.sort(key=lambda m: m.score, reverse=True)

        for move in moves:
            self.board.make_move(move)
            eval_score = self.alphabeta(depth - 1, alpha, beta, False)
            self.board.undo_move()

            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move

            alpha = max(alpha, best_eval)

        return best_move, best_eval