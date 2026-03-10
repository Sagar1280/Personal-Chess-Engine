
# --- Flask backend for React frontend integration ---
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from engine.board import Board
from engine.move_generator import MoveGenerator
from engine.search import Search
from engine.evaluate import Evaluator
from engine.move import Move
from vision.image_to_fen import detect_board
import os

app = Flask(__name__, static_folder="Frontend/build", static_url_path="/")
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 
print("MAX SIZE:", app.config['MAX_CONTENT_LENGTH'])


board = Board()
board.set_up_initial_position()
evaluator = Evaluator()
generator = MoveGenerator(board)
search = Search(board, generator, evaluator)
depth = 3
move_history = []  # Track all moves for undo
start_position_fen = None  # Track the starting FEN (for replaying after undo)

def get_fen():
    """Delegate to the Board's own FEN serializer, which correctly
    includes castling rights, en-passant, and move counters."""
    return board.get_fenn()


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
    promotion = data.get("promotion")

    promotion_map = {
        "q" : 5,
        "r" : 4,
        "b" : 3,
        "n" : 2
    }
    promo_value = None
    if promotion:
        promo_value = promotion_map.get(promotion.lower())
        if promo_value and board.side_to_move == -1:
            promo_value = -promo_value

    move_str = source + target
    # Always recreate generator from the current board state
    # (mirrors what api_engine_move already does)
    generator = MoveGenerator(board)
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

            if promo_value is not None:
                if move.promotion == promo_value:
                    move_obj = move 
                    break
            else:
                if move.promotion is None:
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
    """Load board position from FEN string using board.load_board()"""
    global board, generator, search, move_history

    try:
        # Use the Board class's own load_board method which correctly
        # handles all FEN fields (including en passant as a (row,col) tuple)
        board = Board()
        board.load_board(fen_string)

        # Recreate generator and search against the freshly-loaded board
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

    if move is None:
        status = get_game_status()
        return jsonify({"error": f"No legal moves ({status})", "fen": get_fen(), "status": status}), 200

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
        try:
            board = Board()
            board.load_board(start_position_fen)
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

@app.route("/api/image_to_fen" , methods = ["POST"])
def image_to_fen():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"error": "Empty file"}), 400

    image_bytes = image.read()

    fen = detect_board(image_bytes)

    return jsonify({"fen": fen})

# Serve React frontend
@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True)