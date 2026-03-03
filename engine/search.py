class Search:
    def __init__(self, board, generator, evaluator):
        self.board = board
        self.generator = generator
        self.evaluator = evaluator
        self.tt = {}

        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2

    
    def quiescence(self, alpha, beta) -> float:
        self.nodes_searched += 1
        stand_pat = self.evaluator.evaluate(self.board)

        if self.board.side_to_move == -1:
            stand_pat = -stand_pat

        # Alpha-beta bounding
        if stand_pat >= beta:
            return stand_pat
        
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
                return score
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

    def negamax(self, depth, alpha, beta):
        self.nodes_searched += 1
        alpha_original = alpha

    # ---- TRANSPOSITION TABLE LOOKUP ----
        entry = self.tt.get(self.board.hash)

        if entry is not None and entry["depth"] >= depth:
            self.tt_hits += 1

            if entry["flag"] == self.Exact:
                return entry["value"]

            elif entry["flag"] == self.LowerBound:
                alpha = max(alpha, entry["value"])

            elif entry["flag"] == self.UpperBound:
                beta = min(beta, entry["value"])

            if alpha >= beta:
                return entry["value"]

    # ---- DEPTH 0 → QUIESCENCE ----
        if depth == 0:
            return self.evaluator.evaluate(self.board)

        moves = self.generator.generate_legal_moves()

    # Checkmate / stalemate
        if not moves:
            if self.board.is_in_check(self.board.side_to_move):
                return -100000  # side to move is checkmated
            else:
                return 0  # stalemate

    # ---- MOVE ORDERING ----
        for move in moves:
            move.score = self.score_move(move)

        moves.sort(key=lambda m: m.score, reverse=True)

        value = float('-inf')

        for move in moves:
            self.board.make_move(move)

            score = -self.negamax(depth - 1, -beta, -alpha)

            self.board.undo_move()

            value = max(value, score)
            alpha = max(alpha, score)

            if alpha >= beta:
                break  # beta cutoff

    # ---- TRANSPOSITION STORE ----
        if value <= alpha_original:
            flag = self.UpperBound
        elif value >= beta:
            flag = self.LowerBound
        else:
            flag = self.Exact

        self.tt[self.board.hash] = {
            "value": value,
            "depth": depth,
            "flag": flag
        }

        return value

    def find_best_move(self, depth):
        self.nodes_searched = 0
        self.tt_hits = 0

        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        moves = self.generator.generate_legal_moves()

        # Order root moves too
        for move in moves:
            move.score = self.score_move(move)

        moves.sort(key=lambda m: m.score, reverse=True)

        best_value = float('-inf')

        for move in moves:
            self.board.make_move(move)
            eval_score = -self.negamax(depth - 1, -beta, -alpha)
            self.board.undo_move()

            print(f"Move: {move}, Eval: {eval_score}")

            if eval_score > best_value:
                best_value = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
        

        print(f"Nodes searched: {self.nodes_searched}, TT hits: {self.tt_hits}")
        return best_move, best_value