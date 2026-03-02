from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.evaluate import Evaluator
from engine.search import Search

board = Board()
generator = MoveGenerator(board)
evaluator = Evaluator()
board.load_board("rnb1kbnr/ppp2ppp/8/4q3/8/8/PPP2PPP/RNBQKBNR w KQkq - 0 5")
board.print_board()

moves = generator.generate_legal_moves()
print(moves)

search = Search(board, generator, evaluator)

best_move, score = search.find_best_move(5)
board.make_move(best_move)
board.print_board()

print("Best move:", best_move)
print("Evaluation:", score)