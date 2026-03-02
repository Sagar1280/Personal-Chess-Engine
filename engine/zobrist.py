import random

class Zobrist:
    def __init__(self):
        random.seed(42)

        # 12 piece types × 64 squares
        self.piece_keys = [
            [random.getrandbits(64) for _ in range(64)]
            for _ in range(12)
        ]

        self.side_key = random.getrandbits(64)

        self.castling_keys = {
            'white_kingside': random.getrandbits(64),
            'white_queenside': random.getrandbits(64),
            'black_kingside': random.getrandbits(64),
            'black_queenside': random.getrandbits(64)
        }

        self.en_passant_keys = [random.getrandbits(64) for _ in range(8)]