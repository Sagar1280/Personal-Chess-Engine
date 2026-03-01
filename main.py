from engine.board import Board
from engine.move_generator import MoveGenerator

board = Board()
board.set_up_initial_position()
generator = MoveGenerator(board)

moves = generator.generate_moves()

print("Initial:")
board.print_board()

move = moves[0]
print("Making move:", move)
board.make_move(move)

board.print_board()

print("Undoing move...")
board.undo_move()
board.print_board()