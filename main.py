from engine.board import Board
from engine.move_generator import MoveGenerator

board = Board()
board.set_up_initial_position()
generator = MoveGenerator(board)

moves = generator.generate_moves()  
print(moves)
print("Total moves:", len(moves))