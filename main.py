
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

def get_fen():
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
    global board, generator, search, move_history
    board = Board()
    board.set_up_initial_position()
    evaluator = Evaluator()
    generator = MoveGenerator(board)
    search = Search(board, generator, evaluator)
    move_history = []  # Reset move history
    return jsonify({
        "fen": get_fen(),
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
    global board, generator, search, move_history
    
    if len(move_history) < 2:
        return jsonify({"error": "Cannot undo"}), 400
    
    # Remove last two moves (player move)
    move_history.pop()  
    #setting a small delay of 0.5 sec in python
    delay = 0.5
    import time
    time.sleep(delay)
    move_history.pop()  # Remove engine move

    
    # Recreate board from initial position and replay remaining moves
    board = Board()
    board.set_up_initial_position()
    generator = MoveGenerator(board)
    
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