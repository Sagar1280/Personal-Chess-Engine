
import numpy as np


def image_to_fen(img):
    #shoudl come up wiht a logic soon
    return fen

def detect_board(img):
   fen = image_to_fen(img)
   return fen

def board_to_fen(board):
    """
    Converts board matrix to FEN string
    """

    fen = ""

    for row in board:
        empty = 0

        for piece in row:

            if piece == "":
                empty += 1

            else:
                if empty > 0:
                    fen += str(empty)
                    empty = 0

                fen += piece

        if empty > 0:
            fen += str(empty)

        fen += "/"

    fen = fen[:-1]

    # default game state
    fen += " w KQkq - 0 1"

    return fen