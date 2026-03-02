from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.evaluate import Evaluator
from engine.search import Search

board = Board()
generator = MoveGenerator(board)
evaluator = Evaluator()
board.load_board("rn1q1b1r/ppp1kppp/4b2n/3Q4/8/8/PPPP1PPP/RNB1KBNR b KQ - 5 6")
board.print_board()

search = Search(board, generator, evaluator)
best_move, best_eval = search.find_best_move(3)
board.make_move(best_move)
board.print_board()

print("eval:", best_eval)