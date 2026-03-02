class Search:
    def __init__(self,board,generator,evaluator):
        self.board = board
        self.generator = generator
        self.evaluator = evaluator
    
    def minimax(self,depth,maximizing_player):
        if depth == 0:
            return self.evaluator.evaluate(self.board)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.generator.generate_legal_moves():
                self.board.make_move(move)
                eval = self.minimax(depth - 1, False)
                self.board.undo_move()
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.generator.generate_legal_moves():
                self.board.make_move(move)
                eval = self.minimax(depth - 1, True)
                self.board.undo_move()
                min_eval = min(min_eval, eval)
            return min_eval
    
    def find_best_move(self,depth):
        best_move = None
        best_eval = float('-inf')

        moves = self.generator.generate_legal_moves()

        for move in moves:
            self.board.make_move(move)

            eval_score = self.minimax(depth - 1, False)

            self.board.undo_move()

            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move   
                         
        return best_move, best_eval

