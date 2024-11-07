import { useState, useEffect, useCallback } from "react";
import io from "socket.io-client";
import { fetchBotNames, getBotMove, agentsReset } from "@/api";
import {
  MiniBoardWinner,
  GameWinner,
  convertBoardToNumeric,
  checkBotWinner,
} from "../utils";

const socket = io(
  process.env.NEXT_PUBLIC_API_URL + "/online" || "http://localhost:5000/online"
);

export const useGame = (
  gameMode: string,
  starts: string,
  lobbyId: string | null,
  playerId: string | null,
  userLetter: string | null,
  onlineStarts: string | null,
  totalGames: number,
  resetBoard: boolean
) => {
  // Types
  type Board = string[][][][];
  type MiniBoard = string[][];
  type Turn = "X" | "O";
  type Winner = "X" | "O" | "Draw";
  type Coords = [number, number, number, number];
  type WinningLine = { type: string; index: number };
  type ActiveMiniBoard = [number, number] | null;
  type AgentId = string | null;
  type AgentIdTurn = "X" | "O" | null;
  type PlayedGamesWinners = ("X" | "O" | "Draw")[];
  type WinPercentages = number[];

  // Board information
  const [board, setBoard] = useState<Board>(
    Array.from({ length: 3 }, () =>
      Array.from({ length: 3 }, () =>
        Array.from({ length: 3 }, () => ["", "", ""])
      )
    )
  );
  const [turn, setTurn] = useState<Turn>("X");
  const [lastMove, setLastMove] = useState<Coords | null>(null);
  const [gameWinner, setGameWinner] = useState<Winner | null>(null);
  const [gameOver, setGameOver] = useState(false);
  const [winningLine, setWinningLine] = useState<WinningLine | null>(null);

  // Mini-board information
  const [activeMiniBoard, setActiveMiniBoard] = useState<ActiveMiniBoard>(null);
  const [winners, setWinners] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(null))
  );
  const [disabled, setDisabled] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(false))
  );

  // Bot information
  const [agentId, setAgentId] = useState<AgentId>(null);
  const [agentId2, setAgentId2] = useState<AgentId>(null);
  const [agentIdTurn, setAgentIdTurn] = useState<AgentIdTurn>(null);
  const [agentId2Turn, setAgentId2Turn] = useState<AgentIdTurn>(null);
  const [isBotThinking, setIsBotThinking] = useState(false);
  const [turnsInverted, setTurnsInverted] = useState(false);
  const [playedGames, setPlayedGames] = useState(0);
  const [playedGamesWinners, setPlayedGamesWinners] =
    useState<PlayedGamesWinners>([]);
  const [winPercentages, setWinPercentages] = useState<WinPercentages>([]);
  const TIMEOUT = 0; // TODO: TIMEOUT (replace the "0" [in milliseconds])

  const updateMiniBoardState = useCallback(
    (a: number, b: number, winner: "X" | "O" | "Draw") => {
      setWinners((prev) => {
        const updated = [...prev];
        updated[a][b] = winner;
        return updated;
      });
      setDisabled((prev) => {
        const updated = [...prev];
        updated[a][b] = true;
        return updated;
      });
    },
    []
  );

  const disableFullMiniBoard = useCallback(
    (a: number, b: number) => {
      setDisabled((prev) => {
        const updated = [...prev];
        updated[a][b] = true;
        return updated;
      });

      setWinners((prev) => {
        const updated = [...prev];
        if (!updated[a][b]) {
          const winner = MiniBoardWinner(board[a][b]);
          if (winner) {
            updated[a][b] = winner;
          } else {
            updated[a][b] = "Draw";
          }
        }
        return updated;
      });
    },
    [board]
  );

  const checkOverallGameWinner = useCallback(() => {
    setWinners((prev) => {
      const overallWinner = GameWinner([...prev], (line) =>
        setWinningLine(line)
      );
      if (overallWinner) {
        setGameWinner(overallWinner as "X" | "O" | "Draw");
        setGameOver(true);
        setDisabled(Array.from({ length: 3 }, () => Array(3).fill(true)));
      }
      return prev;
    });
  }, []);

  const makeMove = useCallback(
    (coords: Coords) => {
      const [a, b, c, d] = coords;
      if (gameWinner || gameOver || disabled[a][b] || board[a][b][c][d]) {
        return;
      }

      const updatedBoard = [...board];
      updatedBoard[a][b][c][d] = turn;
      setBoard(updatedBoard);

      // Actualiza el ganador del mini-tablero antes de proceder
      const winner = MiniBoardWinner(updatedBoard[a][b] as MiniBoard);
      if (winner) {
        updateMiniBoardState(a, b, winner);
      }

      // Calcula el próximo mini-tablero y verifica si debe deshabilitarse
      const nextMiniBoard = MiniBoardWinner(updatedBoard[c][d] as MiniBoard);
      if (!disabled[c][d] && !winners[c][d] && !nextMiniBoard) {
        setActiveMiniBoard([c, d]);
      } else {
        setActiveMiniBoard(null);
      }

      // Verifica si el mini-tablero está lleno
      if (updatedBoard[a][b].flat().every((cell) => cell !== "")) {
        disableFullMiniBoard(a, b);
      }

      // Verifica si el juego general tiene un ganador
      checkOverallGameWinner();

      // Configura la última jugada y el próximo turno
      setLastMove(coords);
      setTurn((prev) => (prev === "X" ? "O" : "X"));
    },
    [
      gameWinner,
      gameOver,
      disabled,
      board,
      turn,
      winners,
      checkOverallGameWinner,
      updateMiniBoardState,
      disableFullMiniBoard,
    ]
  );

  const handleCellClick = (a: number, b: number, c: number, d: number) => {
    const coords: Coords = [a, b, c, d];

    if (!isBotThinking && !gameOver) {
      makeMove(coords); // Update the local game state

      if (gameMode === "online") {
        socket.emit("move", {
          lobby_id: lobbyId,
          player_id: playerId,
          move: coords,
        }); // Emit the move to the server
      }
    } else if (gameMode === "player-vs-bot" || gameMode === "bot-vs-bot") {
      alert("Let " + (turn === agentIdTurn ? agentId : agentId2) + " cook.");
    } else if (gameMode === "online" && userLetter !== turn) {
      alert("Wait for your turn.");
    }
  };

  const handleBotMove = useCallback(async () => {
    try {
      setIsBotThinking(true);

      const numericBoard: number[][][][] = convertBoardToNumeric(board);

      const coords: Coords = await getBotMove(
        numericBoard,
        activeMiniBoard,
        turn
      );

      makeMove(coords);

      setIsBotThinking(false);
    } catch (error) {
      setIsBotThinking(true);
      console.error("Error fetching bot's move:", error);
    }
  }, [board, activeMiniBoard, turn, makeMove]);

  const resetGame = useCallback(() => {
    setBoard(
      Array.from({ length: 3 }, () =>
        Array.from({ length: 3 }, () =>
          Array.from({ length: 3 }, () => ["", "", ""])
        )
      )
    );
    setTurn("X");
    setWinners(Array.from({ length: 3 }, () => Array(3).fill(null)));
    setDisabled(Array.from({ length: 3 }, () => Array(3).fill(false)));
    setGameWinner(null);
    setActiveMiniBoard(null);
    setWinningLine(null);
    setTurnsInverted(false);
  }, []);

  const startAgain = useCallback(() => {
    resetGame();
    setGameOver(false);
    setLastMove(null);
    setTurnsInverted(false);
  }, [resetGame]);

  const invertTurns = useCallback(() => {
    setTurn((prev) => {
      const newTurn = prev === "X" ? "O" : "X";
      return newTurn;
    });
    setTurnsInverted(true);
  }, []);

  // Reset game
  useEffect(() => {
    if (resetBoard) {
      resetGame();
    }
  }, [resetBoard, resetGame]);

  // Automatically handle bot move whenever it's the bot's turn
  useEffect(() => {
    if (!turnsInverted && starts === "bot" && turn === "X") {
      invertTurns();
      agentsReset();
    }

    if (gameMode === "player-vs-bot" && turn === "O" && !gameOver) {
      handleBotMove();
    }
  }, [
    gameMode,
    starts,
    gameOver,
    turn,
    turnsInverted,
    handleBotMove,
    invertTurns,
  ]);

  // Bot-vs-Bot
  useEffect(() => {
    if (
      gameMode === "bot-vs-bot" &&
      !gameOver &&
      !isBotThinking &&
      !gameWinner &&
      playedGames < totalGames
    ) {
      if (!turnsInverted) {
        invertTurns();
        agentsReset();
        setAgentIdTurn(() => {
          return turn === "X" ? "O" : "X";
        });
        setAgentId2Turn(() => {
          return turn === "X" ? "X" : "O";
        });
      } else {
        setTimeout(handleBotMove, TIMEOUT);
      }
    }
  }, [
    gameMode,
    totalGames,
    gameOver,
    isBotThinking,
    gameWinner,
    playedGames,
    turn,
    handleBotMove,
    invertTurns,
    turnsInverted,
  ]);

  // Update playedGamesWinners whenever game ends
  useEffect(() => {
    if (gameOver && playedGames < totalGames) {
      agentsReset();
      setPlayedGamesWinners((prev) => [...prev, gameWinner || "Draw"]);
      setPlayedGames((prev) => prev + 1);
      startAgain();
    }
  }, [gameOver, gameWinner, playedGames, totalGames, startAgain]);

  // Set win percentages whenever playedGamesWinners updates
  useEffect(() => {
    if (gameMode === "bot-vs-bot" && playedGamesWinners.length) {
      setWinPercentages(checkBotWinner(playedGamesWinners));
    }
  }, [playedGamesWinners, gameMode]);

  // Bot IDs
  useEffect(() => {
    if (gameMode === "player-vs-bot" || gameMode === "bot-vs-bot") {
      fetchBotNames()
        .then((data) => {
          if (data.agent1_name && data.agent2_name) {
            setAgentId(data.agent1_name);
            setAgentId2(gameMode === "bot-vs-bot" ? data.agent2_name : null);
          } else {
            console.error("Bot names data is missing or invalid", data);
          }
        })
        .catch((error) => console.error("Error in fetchBotNames:", error));
    }
  }, [gameMode]);

  // Online
  useEffect(() => {
    if (gameMode === "online" && onlineStarts) {
      setTurn(onlineStarts as Turn);
    }
  }, [gameMode, onlineStarts]);

  useEffect(() => {
    const handleMove = (data: {
      player_id: string;
      move: [number, number, number, number]; // Ensure this matches the structure sent from the server
    }) => {
      const { move } = data;
      makeMove(move); // Call the makeMove function to update the game state
    };

    socket.on("move", handleMove); // Listen for the move event

    return () => {
      socket.off("move", handleMove); // Clean up the event listener on unmount
    };
  }, [makeMove]);
  return {
    board,
    turn,
    lastMove,
    gameOver,
    activeMiniBoard,
    winners,
    disabled,
    winningLine,
    agentId,
    agentId2,
    agentIdTurn,
    agentId2Turn,
    playedGames,
    winPercentages,
    gameWinner,
    isBotThinking,
    handleCellClick,
    makeMove,
  };
};
