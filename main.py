from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.search import Search
from engine.evaluate import Evaluator
from engine.move import Move


def algebraic_to_index(square):
    col = ord(square[0]) - ord('a')
    row = 8 - int(square[1])
    return row, col


def get_user_move(board, generator):
    legal_moves = generator.generate_legal_moves()

    while True:
        user_input = input("Enter your move (e2e4): ")

        if len(user_input) != 4:
            print("Invalid format.")
            continue

        start = user_input[:2]
        end = user_input[2:]

        start_row, start_col = algebraic_to_index(start)
        end_row, end_col = algebraic_to_index(end)

        for move in legal_moves:
            if (move.start_row == start_row and
                move.start_column == start_col and
                move.end_row == end_row and
                move.end_column == end_col):
                return move

        print("Illegal move. Try again.")


def main():
    board = Board()
    board.set_up_initial_position()

    evaluator = Evaluator()
    generator = MoveGenerator(board)
    search = Search(board, generator, evaluator)

    depth = 4  # adjust strength here

    while True:
        board.print_board()

        if board.side_to_move == 1:
            print("White to move (You)")
            move = get_user_move(board, generator)
        else:
            print("Black to move (Engine)")
            move, eval_score = search.find_best_move(depth)
            print("Engine plays:", move)
            print("Eval:", eval_score)

        board.make_move(move)


if __name__ == "__main__":
    main()