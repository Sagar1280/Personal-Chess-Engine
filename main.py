from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.evaluate import Evaluator
from engine.search import Search

board = Board()
generator = MoveGenerator(board)
evaluator = Evaluator()
board.load_board("r1b1kbnr/pppn1ppp/4p3/1B1q4/8/2N5/PPPP1PPP/R1BQK1NR w KQkq - 2 5")
board.print_board()

moves = generator.generate_legal_moves()

search = Search(board, generator, evaluator)
best_move, best_eval = search.find_best_move(5)
board.make_move(best_move)
board.print_board()

print(f"Number of TT hits : {search.tt_hits}")