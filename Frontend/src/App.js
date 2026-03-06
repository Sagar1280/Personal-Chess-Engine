import React, { useState, useEffect } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import "./App.css";

// Simple beep sounds using Web Audio API
const playErrorSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 300; // Low beep
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
  } catch (e) {
    console.log("Audio not available");
  }
};

const playSuccessSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800; // High beep
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
  } catch (e) {
    console.log("Audio not available");
  }
};

const eloEstimates = {
  1: 800,
  2: 1000,
  3: 1400,
  4: 1800,
  5: 2200,
};

function App() {
  const [gameStarted, setGameStarted] = useState(false);
  const [playerColor, setPlayerColor] = useState(null);
  const [game, setGame] = useState(null);
  const [fen, setFen] = useState("");
  const [gameOver, setGameOver] = useState(false);
  const [boardHighlight, setBoardHighlight] = useState("");
  const [depth, setDepth] = useState(3);
  const [engineThinking, setEngineThinking] = useState(false);
  const [message, setMessage] = useState("");
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [fenInput, setFenInput] = useState("");
  const [uploadedImage, setUploadedImage] = useState(null);

  useEffect(() => {
    if (!game) return;

    if (game.isCheckmate()) {
      setGameOver(true);
      setBoardHighlight("checkmate");
      setMessage(game.turn() === "w" ? "Black wins by checkmate!" : "White wins by checkmate!");
    } else if (game.isStalemate()) {
      setGameOver(true);
      setBoardHighlight("stalemate");
      setMessage("Stalemate!");
    } else {
      setGameOver(false);
      setBoardHighlight("");
      const isPlayerTurn = (playerColor === "white" && game.turn() === "w") || (playerColor === "black" && game.turn() === "b");
      if (!isPlayerTurn && !engineThinking) {
        makeEngineMove();
      }
    }
  }, [fen, game, playerColor, engineThinking]);

  const startGame = async (color) => {
    setPlayerColor(color);
    
    // Reset backend game state
    try {
      const resetResponse = await fetch("http://localhost:5000/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const resetData = await resetResponse.json();
      console.log("Game reset:", resetData);
    } catch (error) {
      setMessage(`Reset error: ${error.message}`);
    }
    
    const newGame = new Chess();
    setGame(newGame);
    setFen(newGame.fen());
    setGameStarted(true);
    setGameOver(false);
    setBoardHighlight("");
    setMessage("");
  };

  const makeEngineMove = async () => {
    setEngineThinking(true);
    try {
      const response = await fetch("http://localhost:5000/api/engine_move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ depth }),
      });
      const data = await response.json();
      if (data.error) {
        setMessage(`Engine error: ${data.error}`);
        setEngineThinking(false);
        return;
      }
      const newGame = new Chess(data.fen);
      setGame(newGame);
      setFen(data.fen);
      playSuccessSound();
    } catch (error) {
      setMessage(`Connection error: ${error.message}`);
    }
    setEngineThinking(false);
  };

  const onDrop = async (sourceSquare, targetSquare) => {
    if (gameOver || engineThinking || !game) return false;

    const isPlayerTurn = (playerColor === "white" && game.turn() === "w") || (playerColor === "black" && game.turn() === "b");
    if (!isPlayerTurn) return false;

    try {
      const move = game.move({ from: sourceSquare, to: targetSquare, promotion: "q" });
      if (move === null) {
        playErrorSound();
        return false;
      }

      try {
        const response = await fetch("http://localhost:5000/api/move", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ from: sourceSquare, to: targetSquare }),
        });

        if (!response.ok) {
          game.undo();
          playErrorSound();
          return false;
        }

        const data = await response.json();
        const newGame = new Chess(data.fen);
        setGame(newGame);
        setFen(data.fen);
        playSuccessSound();
        return true;
      } catch (error) {
        game.undo();
        setMessage(`Connection error: ${error.message}`);
        return false;
      }
    } catch (e) {
      playErrorSound();
      return false;
    }
  };

  const handleUndo = async () => {
    if (!game || gameOver || engineThinking) return;

    try {
      const response = await fetch("http://localhost:5000/api/undo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        setMessage("Cannot undo");
        return;
      }

      const data = await response.json();
      const newGame = new Chess(data.fen);
      setGame(newGame);
      setFen(data.fen);
      setMessage("");
    } catch (error) {
      setMessage(`Undo error: ${error.message}`);
    }
  };

  const resetGame = () => {
    setGameStarted(false);
    setPlayerColor(null);
    setGame(null);
    setFen("");
    setGameOver(false);
    setBoardHighlight("");
    setMessage("");
  };

  if (!gameStarted) {
    return (
      <div className="main-container">
        {/* Left Sidebar */}
        <div className="left-sidebar">
          <div className="sidebar-title">PLAY</div>
        </div>

        {/* Right Panel */}
        <div className="right-panel">
          <div className="button-group">
            <button className="start-game-btn" onClick={() => startGame("white")}>
              Start Game
            </button>
            <button className="load-game-btn" onClick={() => setShowLoadModal(true)}>
              Load Game
            </button>
          </div>
        </div>

        {/* Load Game Modal */}
        {showLoadModal && (
          <div className="modal-overlay" onClick={() => setShowLoadModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Load Game</h2>
                <button className="modal-close" onClick={() => setShowLoadModal(false)}>×</button>
              </div>
              
              <div className="modal-body">
                <div className="image-upload-section">
                  <label>Upload Board Image</label>
                  <div className="image-upload-area">
                    {uploadedImage ? (
                      <img src={uploadedImage} alt="Uploaded board" className="uploaded-image" />
                    ) : (
                      <p>Paste or upload board image here</p>
                    )}
                  </div>
                  <input 
                    type="file" 
                    accept="image/*" 
                    onChange={(e) => {
                      if (e.target.files[0]) {
                        const reader = new FileReader();
                        reader.onload = (event) => setUploadedImage(event.target.result);
                        reader.readAsDataURL(e.target.files[0]);
                      }
                    }}
                  />
                </div>

                <div className="fen-input-section">
                  <label>FEN String</label>
                  <input 
                    type="text" 
                    placeholder="Paste FEN string here"
                    value={fenInput}
                    onChange={(e) => setFenInput(e.target.value)}
                    className="fen-input"
                  />
                </div>

                <button className="load-btn" onClick={() => {
                  // Logic for loading game will be added later
                  console.log("Loading game with FEN:", fenInput);
                  setShowLoadModal(false);
                }}>
                  Load Game
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="main-container-game">
      {/* Left Sidebar */}
      <div className="left-sidebar">
        <div className="sidebar-title">PLAY</div>
      </div>

      {/* Main Game Area */}
      <div className="game-area">
        <div className={`app-container ${boardHighlight}`}>
          <div className="game-info">
            <span className="player-info">You: {playerColor.toUpperCase()}</span>
            <span className="turn-info">{game && !gameOver ? `${game.turn() === "w" ? "White" : "Black"} to move` : ""}</span>
            {engineThinking && <span className="thinking-info">Engine thinking...</span>}
          </div>

          <div className={`chessboard-wrapper ${boardHighlight}`}>
            {game && (
              <Chessboard
                position={fen}
                onPieceDrop={onDrop}
                boardWidth={500}
                animationDuration={200}
                boardOrientation={playerColor === "black" ? "black" : "white"}
              />
            )}
          </div>

          <div className="controls">
            <div className="depth-control">
              <label>Engine Strength (Depth)</label>
              <input
                type="range"
                min="1"
                max="5"
                value={depth}
                onChange={(e) => setDepth(Number(e.target.value))}
                disabled={gameOver}
              />
              <div className="depth-info">
                <span>Depth: {depth}</span>
                <span className="elo-estimate">≈ {eloEstimates[depth]} ELO</span>
              </div>
            </div>

            <button 
              className="undo-btn" 
              onClick={handleUndo}
              disabled={gameOver || engineThinking}
            >
              ↶ Undo Move
            </button>

            {gameOver && (
              <div className="game-over-message">
                <h2>{boardHighlight === "checkmate" ? "Checkmate!" : "Stalemate!"}</h2>
                <p>{message}</p>
                <button onClick={resetGame} className="reset-btn">
                  Play Again
                </button>
              </div>
            )}

            {message && !gameOver && <div className="message">{message}</div>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
