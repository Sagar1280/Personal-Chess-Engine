
# --- Flask backend for React frontend integration ---
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.search import Search
from engine.evaluate import Evaluator
from engine.move import Move
import os

app = Flask(__name__, static_folder="frontend/build", static_url_path="/")
CORS(app)

board = Board()
board.set_up_initial_position()
evaluator = Evaluator()
generator = MoveGenerator(board)
search = Search(board, generator, evaluator)
depth = 3
move_history = []  # Track all moves for undo
start_position_fen = None  # Track the starting FEN (for replaying after undo)

def get_fen():
    """Convert board state to FEN notation"""
    piece_map = {
        1: 'P', -1: 'p',
        2: 'N', -2: 'n',
        3: 'B', -3: 'b',
        4: 'R', -4: 'r',
        5: 'Q', -5: 'q',
        6: 'K', -6: 'k'
    }
    
    fen_parts = []
    for row in board.board:
        fen_row = ""
        empty_count = 0
        for piece in row:
            if piece == 0:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += piece_map.get(piece, '?')
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_parts.append(fen_row)
    
    piece_placement = '/'.join(fen_parts)
    active_color = 'w' if board.side_to_move == 1 else 'b'
    castling = "-"
    en_passant = "-"
    halfmove = 0
    fullmove = board.move_number
    
    return f"{piece_placement} {active_color} {castling} {en_passant} {halfmove} {fullmove}"

def get_game_status():
    # You may need to adjust these based on your engine's API
    if board.is_checkmate():
        return "checkmate"
    elif board.is_stalemate():
        return "stalemate"
    elif board.is_check():
        return "check"
    else:
        return "active"

@app.route("/api/game", methods=["GET"])
def api_game():
    return jsonify({
        "fen": get_fen(),
        "status": get_game_status(),
        "side_to_move": board.side_to_move
    })

@app.route("/api/reset", methods=["POST"])
def api_reset():
    global board, generator, search, move_history, start_position_fen
    board = Board()
    board.set_up_initial_position()
    evaluator = Evaluator()
    generator = MoveGenerator(board)
    search = Search(board, generator, evaluator)
    move_history = []  # Reset move history
    start_position_fen = get_fen()  # Capture initial position FEN
    return jsonify({
        "fen": start_position_fen,
        "status": "active",
        "side_to_move": board.side_to_move
    })

@app.route("/api/move", methods=["POST"])
def api_move():
    global generator, move_history
    data = request.json
    source = data.get("from")
    target = data.get("to")
    move_str = source + target
    legal_moves = generator.generate_legal_moves()

    def algebraic_to_index(square):
        col = ord(square[0]) - ord('a')
        row = 8 - int(square[1])
        return row, col
    start_row, start_col = algebraic_to_index(source)
    end_row, end_col = algebraic_to_index(target)
    move_obj = None
    for move in legal_moves:
        if (move.start_row == start_row and
            move.start_column == start_col and
            move.end_row == end_row and
            move.end_column == end_col):
            move_obj = move
            break
    if move_obj is None:
        return jsonify({"error": "Illegal move"}), 400
    board.make_move(move_obj)
    move_history.append(move_obj)  # Record move in history
    generator = MoveGenerator(board)
    return jsonify({
        "fen": get_fen(),
        "status": get_game_status(),
        "side_to_move": board.side_to_move
    })

def load_board_from_fen(fen_string):
    """Load board position from FEN string"""
    global board, generator, search, move_history
    
    try:
        parts = fen_string.split()
        if len(parts) < 4:
            raise ValueError("Invalid FEN format")
        
        piece_placement = parts[0]
        active_color = parts[1]
        castling = parts[2] if len(parts) > 2 else "-"
        en_passant = parts[3] if len(parts) > 3 else "-"
        halfmove = int(parts[4]) if len(parts) > 4 else 0
        fullmove = int(parts[5]) if len(parts) > 5 else 1
        
        # Create new board
        board = Board()
        
        # Clear the board first
        for i in range(8):
            for j in range(8):
                board.board[i][j] = 0
        
        # Parse piece placement
        piece_chars = {
            'P': 1, 'p': -1,
            'N': 2, 'n': -2,
            'B': 3, 'b': -3,
            'R': 4, 'r': -4,
            'Q': 5, 'q': -5,
            'K': 6, 'k': -6
        }
        
        rows = piece_placement.split('/')
        for row_idx, row_str in enumerate(rows):
            col_idx = 0
            for char in row_str:
                if char.isdigit():
                    col_idx += int(char)
                elif char in piece_chars:
                    board.board[row_idx][col_idx] = piece_chars[char]
                    col_idx += 1
        
        # Set side to move
        board.side_to_move = 1 if active_color == 'w' else -1
        
        # Set castling rights
        board.castling_rights = {
            'white_kingside': 'K' in castling,
            'white_queenside': 'Q' in castling,
            'black_kingside': 'k' in castling,
            'black_queenside': 'q' in castling
        }
        
        # Set en passant
        board.en_passant = en_passant if en_passant != '-' else None
        
        # Set move counters
        board.halfmove_clock = halfmove
        board.move_number = fullmove
        
        # Recreate generator and search
        generator = MoveGenerator(board)
        search = Search(board, generator, Evaluator())
        move_history = []
        
        return True
    except Exception as e:
        raise ValueError(f"Failed to parse FEN: {str(e)}")

@app.route("/api/load_fen", methods=["POST"])
def api_load_fen():
    global board, generator, search, move_history, start_position_fen
    data = request.json
    fen_string = data.get("fen")
    
    if not fen_string:
        return jsonify({"error": "No FEN string provided"}), 400
    
    try:
        load_board_from_fen(fen_string)
        start_position_fen = fen_string  # Capture the loaded FEN as the starting position
           
        return jsonify({ "message": "FEN loaded successfully",
            "fen": get_fen(),
            "status": get_game_status(),
            "side_to_move": board.side_to_move,
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/engine_move", methods=["POST"])
def api_engine_move():
    global generator, move_history
    data = request.json
    depth_param = data.get("depth", 4)
    
    # Recreate generator with current board state
    generator = MoveGenerator(board)
    move, eval_score = search.find_best_move(depth_param)
    board.make_move(move)
    move_history.append(move)  # Record engine move in history
    
    return jsonify({
        "fen": get_fen(),
        "status": get_game_status(),
        "side_to_move": board.side_to_move,
        "move": str(move),
        "eval": eval_score
    })

@app.route("/api/undo", methods=["POST"])
def api_undo():
    global board, generator, search, move_history, start_position_fen
    
    if len(move_history) < 2:
        return jsonify({"error": "Cannot undo"}), 400
    
    # Remove last two moves (player move and engine response)
    move_history.pop()  # Remove engine move
    move_history.pop()  # Remove player move
    
    # Recreate board from start position without resetting move_history
    if start_position_fen:
        # Parse and load the starting FEN directly into board
        try:
            parts = start_position_fen.split()
            piece_placement = parts[0]
            active_color = parts[1]
            castling = parts[2] if len(parts) > 2 else "-"
            en_passant = parts[3] if len(parts) > 3 else "-"
            halfmove = int(parts[4]) if len(parts) > 4 else 0
            fullmove = int(parts[5]) if len(parts) > 5 else 1
            
            # Clear the board
            for i in range(8):
                for j in range(8):
                    board.board[i][j] = 0
            
            # Parse piece placement
            piece_chars = {
                'P': 1, 'p': -1,
                'N': 2, 'n': -2,
                'B': 3, 'b': -3,
                'R': 4, 'r': -4,
                'Q': 5, 'q': -5,
                'K': 6, 'k': -6
            }
            
            rows = piece_placement.split('/')
            for row_idx, row_str in enumerate(rows):
                col_idx = 0
                for char in row_str:
                    if char.isdigit():
                        col_idx += int(char)
                    elif char in piece_chars:
                        board.board[row_idx][col_idx] = piece_chars[char]
                        col_idx += 1
            
            # Set side to move
            board.side_to_move = 1 if active_color == 'w' else -1
            
            # Set castling rights
            board.castling_rights = {
                'white_kingside': 'K' in castling,
                'white_queenside': 'Q' in castling,
                'black_kingside': 'k' in castling,
                'black_queenside': 'q' in castling
            }
            
            # Set en passant
            board.en_passant = en_passant if en_passant != '-' else None
            
            # Set move counters
            board.halfmove_clock = halfmove
            board.move_number = fullmove
        except:
            # Fallback to initial position
            board = Board()
            board.set_up_initial_position()
    else:
        board = Board()
        board.set_up_initial_position()
    
    # Replay all remaining moves from move_history
    for move in move_history:
        board.make_move(move)
    
    # Recreate generator and search for final state
    generator = MoveGenerator(board)
    search = Search(board, generator, Evaluator())
    
    return jsonify({
        "fen": get_fen(),
        "status": get_game_status(),
        "side_to_move": board.side_to_move
    })

# Serve React frontend
@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True)