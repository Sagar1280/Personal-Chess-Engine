from engine.board import Board
from engine.move_generator import MoveGenerator

board = Board()

board.load_board("rnbqkbnr/ppp1p1pp/3p1P2/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 3")
board.print_board()

moves = MoveGenerator(board)

legal_moves = moves.generate_legal_moves()
print(legal_moves)

