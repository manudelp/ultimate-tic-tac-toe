import { useState, useEffect, useCallback, useRef } from "react";
import { getSocket } from "@/socket";
import { Socket } from "socket.io-client";
import { getBotMove, agentsReset } from "@/api";
import {
  MiniBoardWinner,
  GameWinner,
  convertBoardToNumeric,
} from "@/lib/game";
import { toast } from "sonner";

import type { BotInfo, Coords, WinningLine, ActiveMiniBoard } from "@/types/game";

type Turn = "X" | "O";
type Winner = "X" | "O" | "Draw";
type Board = string[][][][];
type MiniBoard = string[][];
type MoveHistory = { turn: Turn; coords: Coords }[];
type MoveData = {
  bigRow: number;
  bigCol: number;
  smallRow: number;
  smallCol: number;
};

interface GameSnapshot {
  board: Board;
  turn: Turn;
  lastMove: Coords | null;
  gameWinner: Winner | null;
  gameOver: boolean;
  winningLine: WinningLine | null;
  moveNumber: number;
  moveHistory: MoveHistory;
  activeMiniBoard: ActiveMiniBoard;
  winners: (string | null)[][];
  disabled: boolean[][];
  gameMode: string;
  botId: number;
  starts: string;
}

const STORAGE_KEY = "uttt_game_state";

function saveGame(snapshot: GameSnapshot) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
  } catch { /* quota exceeded or unavailable */ }
}

function loadGame(gameMode: string, botId: number, starts: string): GameSnapshot | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const snapshot: GameSnapshot = JSON.parse(raw);
    if (snapshot.gameMode !== gameMode || snapshot.botId !== botId || snapshot.starts !== starts) {
      return null;
    }
    return snapshot;
  } catch {
    return null;
  }
}

function clearGame() {
  try { sessionStorage.removeItem(STORAGE_KEY); } catch { /* */ }
}

export const useGame = (
  gameMode: string,
  bot: BotInfo,
  starts: string,
  yourLetter?: string,
  lobbyCode?: string
) => {
  const socketRef = useRef<Socket | null>(null);
  const isRestoredRef = useRef(false);

  const initialBoard = Array.from({ length: 3 }, () =>
    Array.from({ length: 3 }, () =>
      Array.from({ length: 3 }, () => ["", "", ""])
    )
  );

  // Try to restore saved state for non-online games
  const saved = gameMode !== "online" ? loadGame(gameMode, bot.id, starts) : null;

  const [board, setBoard] = useState<Board>(saved?.board ?? initialBoard);
  const [turn, setTurn] = useState<Turn>(saved?.turn ?? (starts === "player" ? "X" : "O") as Turn);
  const [lastMove, setLastMove] = useState<Coords | null>(saved?.lastMove ?? null);
  const [gameWinner, setGameWinner] = useState<Winner | null>(saved?.gameWinner ?? null);
  const [gameOver, setGameOver] = useState(saved?.gameOver ?? false);
  const [winningLine, setWinningLine] = useState<WinningLine | null>(saved?.winningLine ?? null);
  const [moveNumber, setMoveNumber] = useState(saved?.moveNumber ?? 0);
  const [moveHistory, setMoveHistory] = useState<MoveHistory>(saved?.moveHistory ?? []);
  const [activeMiniBoard, setActiveMiniBoard] = useState<ActiveMiniBoard>(saved?.activeMiniBoard ?? null);
  const [winners, setWinners] = useState(saved?.winners ?? Array.from({ length: 3 }, () => Array(3).fill(null)));
  const [disabled, setDisabled] = useState(saved?.disabled ?? Array.from({ length: 3 }, () => Array(3).fill(false)));

  const [isBotThinking, setIsBotThinking] = useState(false);
  const [timeToMove, setTimeToMove] = useState<number>(0.0);
  const isBotThinkingRef = useRef(false);

  if (saved && !isRestoredRef.current) {
    isRestoredRef.current = true;
  }

  // Persist state after every change (non-online only)
  useEffect(() => {
    if (gameMode === "online") return;
    saveGame({
      board, turn, lastMove, gameWinner, gameOver, winningLine,
      moveNumber, moveHistory, activeMiniBoard, winners, disabled,
      gameMode, botId: bot.id, starts,
    });
  }, [board, turn, lastMove, gameWinner, gameOver, winningLine, moveNumber, moveHistory, activeMiniBoard, winners, disabled, gameMode, bot.id, starts]);

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
      let capturedWinningLine: WinningLine | null = null;

      const overallWinner = GameWinner([...prev], (line) => {
        capturedWinningLine = line;
        setWinningLine(line);
      });

      if (overallWinner) {
        setGameWinner(overallWinner as "X" | "O" | "Draw");
        setGameOver(true);

        const winnerSound = new Audio("/assets/sounds/win.mp3");
        winnerSound.volume = 0.2;
        winnerSound.play();

        setDisabled(Array.from({ length: 3 }, () => Array(3).fill(true)));

        if (gameMode === "online" && lobbyCode && socketRef.current) {
          socketRef.current.emit("gameOver", {
            code: lobbyCode,
            winner: overallWinner,
            winningLine: capturedWinningLine,
          });
        }
      }
      return prev;
    });
  }, [gameMode, lobbyCode]);

  const makeMove = useCallback(
    (coords: Coords, forcedLetter?: "X" | "O", emitMove = true) => {
      const [a, b, c, d] = coords;

      if (gameWinner || gameOver || disabled[a][b] || board[a][b][c][d]) {
        return;
      }

      const currentTurn = forcedLetter || turn;

      setTurn((prev) => (prev === "X" ? "O" : "X"));
      setLastMove(coords);
      setMoveNumber((prev) => prev + 1);
      setMoveHistory((prev) => [...prev, { turn: currentTurn, coords }]);

      setBoard((prevBoard) => {
        const newBoard = JSON.parse(JSON.stringify(prevBoard));
        newBoard[a][b][c][d] = currentTurn;

        const winner = MiniBoardWinner(newBoard[a][b] as MiniBoard);
        if (winner) {
          updateMiniBoardState(a, b, winner);
        }

        const nextMiniBoard = MiniBoardWinner(newBoard[c][d] as MiniBoard);
        if (!disabled[c][d] && !winners[c][d] && !nextMiniBoard) {
          setActiveMiniBoard([c, d]);
        } else {
          setActiveMiniBoard(null);
        }

        if (newBoard[a][b].flat().every((cell: string) => cell !== "")) {
          disableFullMiniBoard(a, b);
        }

        checkOverallGameWinner();

        return newBoard;
      });

      setTimeout(() => {
        try {
          const tapSound = new Audio("/assets/sounds/tap.mp3");
          tapSound.volume = 0.25;
          tapSound.play().catch(() => {});
        } catch (error) {
          console.error("Error playing sound:", error);
        }

        if (
          gameMode === "online" &&
          lobbyCode &&
          emitMove &&
          socketRef.current
        ) {
          socketRef.current.emit("makeMove", {
            code: lobbyCode,
            move: { bigRow: a, bigCol: b, smallRow: c, smallCol: d },
          });
        }
      }, 0);
    },
    [
      gameWinner, gameOver, disabled, board, turn, winners,
      checkOverallGameWinner, updateMiniBoardState, disableFullMiniBoard,
      gameMode, lobbyCode,
    ]
  );

  const handleCellClick = (a: number, b: number, c: number, d: number) => {
    if (gameOver) return;

    const coords: Coords = [a, b, c, d];

    if (board[a][b][c][d]) {
      toast.warning("This cell is already occupied!");
      return;
    }

    if (gameMode === "online" && turn !== yourLetter) {
      toast.warning("Not your turn!");
      return;
    }

    if (gameMode === "player-vs-bot" && isBotThinking) {
      toast.error("Let " + bot?.name + " " + bot?.icon + " cook.");
      return;
    }

    makeMove(coords);
  };

  const handleBotMove = useCallback(async () => {
    let interval: NodeJS.Timeout | null = null;
    try {
      const startTime = performance.now();

      interval = setInterval(() => {
        const elapsedTime = (performance.now() - startTime) / 1000;
        setTimeToMove(elapsedTime);
      }, 39);

      const numericBoard: number[][][][] = convertBoardToNumeric(board);

      const coords: Coords = await getBotMove(
        bot.id,
        numericBoard,
        activeMiniBoard,
        turn
      );

      makeMove(coords);
    } catch (error) {
      console.error("Error fetching bot's move:", error);
    } finally {
      if (interval) clearInterval(interval);
      setIsBotThinking(false);
    }
  }, [board, bot, activeMiniBoard, turn, makeMove]);

  const handleOpponentMove = useCallback(
    (moveData: MoveData, opponentLetter: "X" | "O") => {
      if (typeof moveData === "string") return;
      if (!moveData) return;

      let move = moveData;
      if (typeof moveData === "object" && moveData !== null && "move" in moveData) {
        move = moveData.move as MoveData;
      }

      let moveArray: [number, number, number, number];

      if (Array.isArray(move)) {
        if (move.length < 4) return;
        moveArray = [Number(move[0]), Number(move[1]), Number(move[2]), Number(move[3])];
      } else if (typeof move === "object" && move !== null) {
        if (move.bigRow === undefined || move.bigCol === undefined || move.smallRow === undefined || move.smallCol === undefined) return;
        moveArray = [Number(move.bigRow), Number(move.bigCol), Number(move.smallRow), Number(move.smallCol)];
      } else {
        return;
      }

      if (!moveArray.every((coord) => typeof coord === "number" && !isNaN(coord))) return;

      makeMove(moveArray, opponentLetter, false);
    },
    [makeMove]
  );

  const resetGame = () => {
    setBoard(initialBoard);
    setTurn((starts === "player" ? "X" : "O") as Turn);
    setLastMove(null);
    setGameWinner(null);
    setGameOver(false);
    setWinningLine(null);
    setMoveNumber(0);
    setActiveMiniBoard(null);
    setWinners(Array.from({ length: 3 }, () => Array(3).fill(null)));
    setDisabled(Array.from({ length: 3 }, () => Array(3).fill(false)));
    setIsBotThinking(false);
    setTimeToMove(0);
    setMoveHistory([]);
    clearGame();
  };

  // Restart bot on new game
  useEffect(() => {
    if (gameMode === "player-vs-bot" && !lastMove) {
      agentsReset(bot.id);
    }
  }, [gameMode, bot, lastMove]);

  // Bot auto-move
  useEffect(() => {
    if (
      gameMode === "player-vs-bot" &&
      ((starts === "player" && turn === "O") ||
        (starts === "bot" && turn === "X")) &&
      !isBotThinkingRef.current &&
      !gameOver
    ) {
      isBotThinkingRef.current = true;
      setIsBotThinking(true);
      handleBotMove().finally(() => {
        isBotThinkingRef.current = false;
        setIsBotThinking(false);
      });
    }
  }, [turn, starts, gameMode, handleBotMove, gameOver]);

  // Online mode socket events
  useEffect(() => {
    if (gameMode === "online") {
      socketRef.current = getSocket();
      const socket = socketRef.current;
      const opponentLetter = yourLetter === "X" ? "O" : "X";

      socket.on("opponentMove", (move) => {
        handleOpponentMove(move, opponentLetter);
      });

      socket.on("opponentLeft", () => {
        toast.error("Your opponent has left the game", { duration: 3000 });
        setTimeout(() => { window.location.href = "/"; }, 3000);
      });

      return () => {
        socket.off("opponentMove");
        socket.off("gameOver");
        socket.off("opponentLeft");
      };
    }
  }, [gameMode, handleOpponentMove, yourLetter]);

  // Clear saved state on exit (when component unmounts for online)
  useEffect(() => {
    return () => {
      if (gameMode === "online") clearGame();
    };
  }, [gameMode]);

  return {
    board, turn, lastMove, activeMiniBoard, winners, disabled,
    winningLine, gameWinner, isBotThinking, moveNumber, timeToMove,
    gameOver, moveHistory, handleCellClick, makeMove, resetGame,
  };
};
