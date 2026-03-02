from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.evaluate import Evaluator
from engine.search import Search

board = Board()
generator = MoveGenerator(board)
evaluator = Evaluator()
board.load_board("rnb1kbnr/pppp2pp/4p3/1N3p1q/3P4/4B3/PPP1PPPP/R2QKBNR w KQkq - 3 5")
board.print_board()

search = Search(board, generator, evaluator)
best_move, best_eval = search.find_best_move(5)
board.make_move(best_move)
board.print_board()

print("eval:", best_eval)