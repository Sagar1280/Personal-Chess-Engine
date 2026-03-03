from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.evaluate import Evaluator
from engine.search import Search

board = Board()
generator = MoveGenerator(board)
evaluator = Evaluator()
board.load_board("rnb1kbnr/pp2pppp/2p5/1B4N1/5q2/8/PPPP1PPP/R1BQK1NR w KQkq - 0 7")
board.print_board()

search = Search(board, generator, evaluator)
best_move, best_eval = search.find_best_move(5)
print("Best move selected:", best_move)
board.make_move(best_move)
board.print_board()


print("eval:", best_eval)