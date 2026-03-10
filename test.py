from engine.board import Board
from engine.move_generator import MoveGenerator

board =  Board()
board.load_board("4k3/PP6/8/8/8/8/8/4K3 w KQkq - 0 1")
generator = MoveGenerator(board)

legal_moves  = generator.generate_legal_moves()

print(legal_moves)
