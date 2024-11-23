import { useState, useEffect, useCallback } from "react";
import { getBotMove, agentsReset } from "@/api";
import { MiniBoardWinner, GameWinner, convertBoardToNumeric } from "../utils";

interface BotListResponse {
  id: number;
  name: string;
  icon: string;
}

export const useGame = (
  gameMode: string,
  bot: BotListResponse,
  starts: string
) => {
  // Types
  type Board = string[][][][];
  type MiniBoard = string[][];
  type Turn = "X" | "O";
  type Winner = "X" | "O" | "Draw";
  type Coords = [number, number, number, number];
  type WinningLine = { type: string; index: number };
  type ActiveMiniBoard = [number, number] | null;

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
  const [moveNumber, setMoveNumber] = useState(0);

  // Mini-board information
  const [activeMiniBoard, setActiveMiniBoard] = useState<ActiveMiniBoard>(null);
  const [winners, setWinners] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(null))
  );
  const [disabled, setDisabled] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(false))
  );

  // Bot information
  const [isBotThinking, setIsBotThinking] = useState(false);
  const [timeToMove, setTimeToMove] = useState<number>(0.0);

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
      setMoveNumber((prev) => prev + 1);
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
      makeMove(coords);
    } else if (gameMode === "player-vs-bot") {
      alert("Let " + bot?.name + " cook.");
    } else {
      alert("Wait for your turn.");
    }
  };

  const handleBotMove = useCallback(async () => {
    try {
      const startTime = performance.now();
      let interval: NodeJS.Timeout;

      // eslint-disable-next-line prefer-const
      interval = setInterval(() => {
        const elapsedTime = (performance.now() - startTime) / 1000;
        setTimeToMove(elapsedTime);
      }, 10);

      setIsBotThinking(true);

      const numericBoard: number[][][][] = convertBoardToNumeric(board);

      const coords: Coords = await getBotMove(
        bot.id,
        numericBoard,
        activeMiniBoard,
        turn
      );

      makeMove(coords);

      setIsBotThinking(false);

      clearInterval(interval);
    } catch (error) {
      setIsBotThinking(true);
      console.error("Error fetching bot's move:", error);
    }
  }, [board, bot, activeMiniBoard, turn, makeMove]);

  // Restart bot move each game
  useEffect(() => {
    return () => {
      if (gameMode === "player-vs-bot" && !lastMove) {
        agentsReset(bot.id);
      }
    };
  }, [gameMode, bot, lastMove]);

  // Automatically handle bot move whenever it's the bot's turn
  useEffect(() => {
    if (
      gameMode === "player-vs-bot" &&
      ((starts === "player" && turn === "O") ||
        (starts === "bot" && turn === "X")) &&
      !isBotThinking &&
      !gameOver
    ) {
      handleBotMove();
    }
  }, [turn, starts, gameMode, handleBotMove, gameOver, isBotThinking]);
  return {
    board,
    turn,
    lastMove,
    activeMiniBoard,
    winners,
    disabled,
    winningLine,
    gameWinner,
    isBotThinking,
    moveNumber,
    timeToMove,
    gameOver,
    handleCellClick,
    makeMove,
  };
};
