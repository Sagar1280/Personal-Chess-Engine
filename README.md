# ♟️ Personal Chess Engine

A fully custom **chess engine** built from scratch in Python, paired with a modern React frontend and a Flask REST API backend. The engine implements classical AI search techniques — evolving from basic Minimax all the way to **Negamax with Alpha-Beta pruning, Quiescence Search, Move Ordering, and a Transposition Table** — and uses **computer vision** to detect board positions from images.

---

## 📋 Table of Contents

- [Demo & Features](#-demo--features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Engine Deep Dive](#-engine-deep-dive)
  - [Board Representation](#board-representation)
  - [Move Generation](#move-generation)
  - [Algorithm Evolution: Minimax → Alpha-Beta → Negamax](#algorithm-evolution-minimax--alpha-beta--negamax)
  - [Quiescence Search](#quiescence-search)
  - [Move Ordering](#move-ordering)
  - [Transposition Table & Zobrist Hashing](#transposition-table--zobrist-hashing)
  - [Evaluation Function](#evaluation-function)
- [Python vs C++ Performance](#-python-vs-c-performance)
- [Computer Vision — Board Detection](#-computer-vision--board-detection)
- [Installation & Setup](#-installation--setup)
- [Running the Project](#-running-the-project)
- [API Reference](#-api-reference)

---

## 🎮 Demo & Features

- Play against the chess engine at **5 difficulty levels** (Depth 1–5, ~800–2200 ELO estimated)
- **Load a game** by pasting a FEN string or uploading a photo of a chess board
- **Pawn promotion** dialog for piece selection (Queen, Rook, Bishop, Knight)
- **Undo move** (undoes both your move and the engine's response)
- **Check / Checkmate / Stalemate** detection with visual and audio feedback
- FEN serialization with castling rights, en passant, half-move clock, and full move number

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Chess Engine** | Python 3.x (custom-built, no chess libraries) |
| **Backend API** | Flask + Flask-CORS |
| **Computer Vision** | Custom CNN / image-to-FEN pipeline |
| **Frontend** | React (Create React App) |
| **Chess UI** | `react-chessboard` |
| **Chess Logic (Frontend)** | `chess.js` (used only for move validation display) |
| **Styling** | Vanilla CSS |
| **Communication** | REST API (JSON over HTTP) |

---

## 📁 Project Structure

```
ChessEngine/
│
├── engine/                  # Core chess engine (pure Python)
│   ├── board.py             # Board state, make/undo move, FEN load/save
│   ├── move.py              # Move dataclass
│   ├── move_generator.py    # Legal move generation for all piece types
│   ├── search.py            # Negamax + Alpha-Beta + Quiescence + TT
│   ├── evaluate.py          # Static position evaluation + piece-square tables
│   └── zobrist.py           # Zobrist hashing for transposition table keys
│
├── vision/                  # Computer vision pipeline
│   ├── image_to_fen.py      # Entry point: image bytes → FEN string
│   └── predict.py           # Model inference
│
├── Frontend/                # React frontend
│   ├── public/
│   └── src/
│       ├── App.js           # Main component, game logic, API calls
│       └── App.css          # Styling
│
├── main.py                  # Flask REST API server
├── test.py                  # Engine testing / benchmark scripts
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🧠 Engine Deep Dive

### Board Representation

The board is stored as a plain **8×8 Python list of integers**:

```
 0  = empty square
 1  = White Pawn       -1  = Black Pawn
 2  = White Knight     -2  = Black Knight
 3  = White Bishop     -3  = Black Bishop
 4  = White Rook       -4  = Black Rook
 5  = White Queen      -5  = Black Queen
 6  = White King       -6  = Black King
```

`board[0][0]` is **a8** (top-left from White's perspective). Row 0 = rank 8, Row 7 = rank 1.

The `Board` class also tracks:
- `side_to_move` (+1 = White, -1 = Black)
- `castling_rights` — dictionary for all four castling options
- `en_passant` — the target square as a `(row, col)` tuple
- `halfmove_clock` — for the 50-move rule
- `move_number`
- `move_history` — stack of `(move, piece, captured, castling, en_passant, clock, number, hash)` tuples enabling O(1) undo

---

### Move Generation

`MoveGenerator` generates pseudo-legal moves for every piece type, then filters to **legal moves** by making each move and checking if the king remains safe:

| Piece | Method |
|---|---|
| Pawn | Push 1, push 2 from start rank, diagonal captures, **promotion** (Q/R/B/N for all 4) |
| Knight | 8 fixed L-shaped offsets |
| Bishop | Diagonal ray sliding (stops on capture or block) |
| Rook | Horizontal/vertical ray sliding |
| Queen | Bishop + Rook combined directions |
| King | 8 one-step moves, plus castling |
| Castling | Checks rights, empty squares, and does NOT check through attacked squares at runtime (handled by legality filter) |

```python
def generate_legal_moves(self):
    legal_moves = []
    for move in self.generate_moves():
        self.board.make_move(move)
        if not self.board.is_in_check(-self.board.side_to_move):
            legal_moves.append(move)
        self.board.undo_move()
    return legal_moves
```

---

### Algorithm Evolution: Minimax → Alpha-Beta → Negamax

#### 1️⃣ Minimax (Starting Point)

The naive starting algorithm. Two separate recursive functions — one for the maximising player (White), one for the minimising player (Black). Every node in the game tree is fully explored.

```
Nodes searched at depth 4: ~100,000–500,000 (completely impractical for deeper searches)
```

**Problem**: Exponential blowup. For a branching factor of ~30, depth 4 means 30⁴ ≈ 810,000 nodes.

#### 2️⃣ Alpha-Beta Pruning

An optimisation layered on top of Minimax. Two bounds are passed through the recursion:
- **Alpha** — the best score the maximiser is *guaranteed* to achieve
- **Beta** — the best score the minimiser is *guaranteed* to achieve

If at any point `alpha >= beta` (**a "beta cutoff"**), the current branch cannot influence the final result and is pruned entirely.

```
Theoretical best case: reduces nodes from O(b^d) to O(b^(d/2))
→ effectively doubles the search depth for the same compute budget
```

**Problem**: Two separate Max/Min functions are still messy and hard to extend.

#### 3️⃣ Negamax (Current Implementation)

Negamax is an elegant reformulation of Alpha-Beta that exploits the **zero-sum** nature of chess: the score for the side to move is always the negation of the score for the other side.

Every recursive call maximises from the perspective of the current player. No separate `min` logic needed:

```python
def negamax(self, depth, alpha, beta):
    if depth == 0:
        return self.evaluator.evaluate(self.board)  # relative to side to move

    moves = self.generator.generate_legal_moves()

    if not moves:
        if self.board.is_in_check(self.board.side_to_move):
            return -100000  # Checkmate
        return 0             # Stalemate

    value = float('-inf')
    for move in moves:
        self.board.make_move(move)
        score = -self.negamax(depth - 1, -beta, -alpha)  # ← the key negation
        self.board.undo_move()

        value = max(value, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break  # Beta cutoff — prune remaining moves

    return value
```

**Result**: Clean, symmetric, easily extended with further optimisations.

---

### Quiescence Search

At depth 0, the engine doesn't blindly return the static evaluation. Instead it enters **quiescence search** — it continues searching **capture-only** moves until the position is "quiet" (no more captures available). This prevents the **horizon effect** — the engine thinking a position is great right before it loses a piece on the next move.

```python
def quiescence(self, alpha, beta):
    stand_pat = self.evaluator.evaluate(self.board)
    if stand_pat >= beta:
        return stand_pat   # Already too good → prune
    alpha = max(alpha, stand_pat)

    for move in sorted_captures:
        self.board.make_move(move)
        score = -self.quiescence(-beta, -alpha)
        self.board.undo_move()
        ...
    return alpha
```

---

### Move Ordering

Alpha-Beta pruning is most effective when the **best moves are searched first** (causing early cutoffs). The engine scores and sorts moves before searching:

| Priority | Move Type | Score |
|---|---|---|
| 1st | Pawn promotes to Queen | 9500 |
| 2nd | Other promotions | 9000 |
| 3rd | Captures (MVV-LVA) | `10000 + 10×victim_value - attacker_value` |
| 4th | Moves that give check | 50 |
| Default | Quiet moves | 0 |

**MVV-LVA** (Most Valuable Victim – Least Valuable Attacker): prefer capturing a Queen with a Pawn over capturing a Pawn with a Queen.

---

### Transposition Table & Zobrist Hashing

The same chess position can be reached via different move sequences (**transpositions**). Without a TT, the engine recomputes the same positions many times.

**Zobrist Hashing** assigns a unique random 64-bit integer to:
- Each of the 12 piece types on each of the 64 squares → `12 × 64 = 768` keys
- Side to move → 1 key
- Castling rights → 4 keys  
- En passant file → 8 keys

The full board hash is computed by **XOR-ing** the relevant keys together. When a move is made/undone, the hash is updated **incrementally** (XOR the old piece out, XOR the new piece in) in O(1) time — not recomputed from scratch.

```python
# In Board.make_move():
self.hash ^= self.zobrist.piece_keys[piece_index][start_square]  # remove piece from start
self.hash ^= self.zobrist.piece_keys[piece_index][end_square]    # add piece to end
self.hash ^= self.zobrist.side_key                               # flip side to move
```

The **Transposition Table** stores `{ hash → (value, depth, flag) }` where `flag` is one of:
- `Exact` — the stored value is the true minimax value
- `LowerBound` — a beta cutoff occurred; actual value is ≥ stored
- `UpperBound` — an alpha cutoff occurred; actual value is ≤ stored

---

### Evaluation Function

The static evaluator returns the score **relative to the side to move** (positive = good for current player):

#### Piece Values (centipawns)

| Piece | Value |
|---|---|
| Pawn | 100 |
| Knight | 320 |
| Bishop | 330 |
| Rook | 500 |
| Queen | 900 |
| King | 20000 |

#### Piece-Square Tables (PST)

Each piece type has an 8×8 bonus/penalty table encoding positional knowledge:
- **Pawns**: Reward advancement and central control, penalise blockage
- **Knights**: Strongly prefer central squares, penalise rim/corner
- **Bishops**: Prefer long diagonals and central influence
- **Rooks**: Reward open files and the 7th rank
- **Queens**: Prefer central development in the endgame
- **King**: Two separate tables — **middlegame** (stay safe, prefer castled position) and **endgame** (centralise and become active)

#### Endgame Detection

When total material on the board drops below **1500 centipawns** (approximately both queens gone), the king switches to its endgame PST to promote active king play.

#### Castling Incentive

The engine adds a +50 bonus before move 15 if the king has castled, and a -25 penalty if the king lingers in the centre past move 12.

---

## ⚡ Python vs C++ Performance

This engine is written in **pure Python**. Here's an honest comparison with what a C++ engine would achieve:

| Metric | This Engine (Python) | Typical C++ Engine |
|---|---|---|
| Nodes/second (depth 4) | ~50,000–150,000 | ~5,000,000–50,000,000 |
| Time for depth 4 search | ~1–4 seconds | < 0.1 seconds |
| Time for depth 6 search | 30–120 seconds | ~0.5–2 seconds |
| Memory overhead | High (Python objects) | Very low (raw arrays/bitboards) |
| Bitboard support | ❌ Not used | ✅ Native 64-bit ints |

### Why the Gap Exists

1. **Python interpreter overhead**: Python is an interpreted language. Every integer operation, list access, and function call goes through the CPython interpreter, adding overhead vs compiled C++ machine code.

2. **No bitboards**: Professional engines represent piece positions as **64-bit integers (bitboards)** where each bit = one square. This allows using fast CPU bitwise operations (`AND`, `OR`, `XOR`, `bit_count`) to generate moves for many squares simultaneously. Python's `int` type is arbitrary precision — not fixed 64-bit — making this inefficient.

3. **Dynamic typing**: Python resolves types at runtime; C++ resolves at compile time.

4. **Memory layout**: Python objects are heap-allocated with reference counting. C++ engines can use stack-allocated arrays with cache-friendly memory layouts.

### What Could Be Done

- **Cython**: Compile Python-like code to C extensions → ~5–10× speedup
- **PyPy**: JIT-compiled Python → ~3–5× speedup
- **C extension module**: Write the hot paths (search, move gen) in C and call from Python
- **Full C++ rewrite**: The standard approach for serious engines (Stockfish, Leela, etc.)

Despite the speed difference, at depth 3–4 the engine plays reasonable club-level chess (~1400 ELO) and responds within a few seconds on a modern machine.

---

## 👁️ Computer Vision — Board Detection

The `/api/image_to_fen` endpoint accepts a photo of a physical or digital chess board and returns a **FEN string** representing the detected position:

1. The image is sent as multipart form data to Flask
2. `vision/image_to_fen.py` runs the detection pipeline (`detect_board()`)
3. A trained CNN classifies each of the 64 squares into one of 13 classes (12 pieces + empty)
4. The predicted piece arrangement is serialised into a standard FEN string
5. The FEN is loaded into both the frontend (`chess.js`) and the backend engine

---

## 📦 Installation & Setup

### Prerequisites

- Python **3.9+**
- Node.js **16+** and npm
- Git

### 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ChessEngine.git
cd ChessEngine
```

### 2 — Set Up Python Virtual Environment

Using a **virtual environment** keeps project dependencies isolated from your system Python.

```bash
# Create the virtual environment (one time only)
python -m venv venv

# Activate it — Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate it — Windows (Command Prompt)
venv\Scripts\activate.bat

# Activate it — macOS / Linux
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt confirming it's active.

### 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

Core Python dependencies:

| Package | Purpose |
|---|---|
| `flask` | REST API server |
| `flask-cors` | Allow React frontend to call the API |
| `numpy` | Array operations for vision pipeline |
| `torch` / `torchvision` | CNN inference for board detection |
| `Pillow` | Image loading and preprocessing |

### 4 — Install Frontend Dependencies

```bash
cd Frontend
npm install
cd ..
```

---

## 🚀 Running the Project

You need **two terminal windows** running simultaneously.

### Terminal 1 — Start the Flask Backend

```bash
# Make sure your venv is activated first!
.\venv\Scripts\Activate.ps1   # Windows

python main.py
```

The API server starts at `http://localhost:5000`.

### Terminal 2 — Start the React Frontend

```bash
cd Frontend
npm start
```

The frontend starts at `http://localhost:3000` and opens automatically in your browser.

> **Note**: The React frontend proxies API calls to `http://localhost:5000`. Both servers must be running at the same time.

---

## 📡 API Reference

All endpoints are served by Flask at `http://localhost:5000`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/game` | Get current board FEN and game status |
| `POST` | `/api/reset` | Reset to the starting position |
| `POST` | `/api/move` | Make a player move `{ from, to, promotion? }` |
| `POST` | `/api/engine_move` | Ask the engine to make a move `{ depth }` |
| `POST` | `/api/undo` | Undo the last two moves (player + engine) |
| `POST` | `/api/load_fen` | Load a position from a FEN string `{ fen }` |
| `POST` | `/api/image_to_fen` | Upload board image → returns FEN string |

### Example: Making a Move

```json
POST /api/move
{
  "from": "e2",
  "to": "e4",
  "promotion": null
}
```

Response:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "status": "active",
  "side_to_move": -1
}
```

### FEN Format

The engine uses the standard **Forsyth–Edwards Notation**:

```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
│                                              │ │    │ │ └─ full move number
│                                              │ │    │ └─── halfmove clock (50-move rule)
│                                              │ │    └───── en passant square ("-" if none)
│                                              │ └────────── castling rights
│                                              └──────────── side to move (w/b)
└─────────────────────────────────────────────────────────── piece placement (rank 8 → rank 1)
```

---

## 🔧 Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```

---

## 📝 Notes & Known Limitations

- **En passant** capture is tracked in FEN but the move generator does not yet generate en passant moves (future work)
- The engine does not implement **time management** (it always searches to the configured depth)
- No **opening book** — the engine plays original moves from move 1
- The transposition table grows unbounded in memory during a session (no eviction policy)
- The computer vision model accuracy depends on image quality and board style

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push and open a Pull Request

---

*Built with ❤️ as a learning project in chess engine development, AI search algorithms, and full-stack web development.*
