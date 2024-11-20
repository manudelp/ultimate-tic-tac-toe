import { useState, useEffect, useCallback } from "react";
import { getBotMove, agentsReset } from "@/api";
import {
  MiniBoardWinner,
  GameWinner,
  convertBoardToNumeric,
  checkBotWinner,
} from "../utils";

interface BotListResponse {
  id: number;
  name: string;
  icon: string;
}

export const useGame = (
  gameMode: string,
  bot: BotListResponse,
  bot2: BotListResponse,
  starts: string,
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
  type AgentIdTurn = "X" | "O" | null;
  type PlayedGamesWinners = ("X" | "O" | "Draw")[];
  type WinPercentages = number[];

  // Game
  const [isPaused, setIsPaused] = useState(false);

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
  const [moveNumber, setMoveNumber] = useState(0); // New state variable for move number

  // Mini-board information
  const [activeMiniBoard, setActiveMiniBoard] = useState<ActiveMiniBoard>(null);
  const [winners, setWinners] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(null))
  );
  const [disabled, setDisabled] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(false))
  );

  // Bot information
  const [agentIdTurn, setAgentIdTurn] = useState<AgentIdTurn>(null);
  const [isBotThinking, setIsBotThinking] = useState(false);
  const [turnsInverted, setTurnsInverted] = useState(false);
  const [timeToMove, setTimeToMove] = useState<number>(0.0);
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
    } else if (gameMode === "player-vs-bot" || gameMode === "bot-vs-bot") {
      alert("Let " + bot?.name + " cook.");
    } else {
      alert("Wait for your turn.");
    }
  };

  const handleBotMove = useCallback(async () => {
    try {
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
    } catch (error) {
      setIsBotThinking(true);
      console.error("Error fetching bot's move:", error);
    }
  }, [board, bot, activeMiniBoard, turn, makeMove]);

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
    setMoveNumber(0);
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

  const togglePlayPause = () => {
    setIsPaused((prev) => !prev);
  };

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
      agentsReset(bot, bot2);
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
    bot,
    bot2,
  ]);

  // Bot-vs-Bot
  useEffect(() => {
    if (
      gameMode === "bot-vs-bot" &&
      !gameOver &&
      !isBotThinking &&
      !gameWinner &&
      playedGames < totalGames &&
      !isPaused
    ) {
      if (!turnsInverted) {
        invertTurns();
        agentsReset(bot, bot2);
        setAgentIdTurn(() => {
          return turn === "X" ? "O" : "X";
        });
      } else {
        const startTime = Date.now();
        const intervalId = setInterval(() => {
          setTimeToMove((Date.now() - startTime) / 1000);
        }, TIMEOUT);

        setTimeout(async () => {
          await handleBotMove();
          clearInterval(intervalId);
          setTimeToMove((Date.now() - startTime) / 1000);
        }, TIMEOUT);
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
    isPaused,
    bot,
    bot2,
  ]);

  // Update playedGamesWinners whenever game ends
  useEffect(() => {
    if (gameOver && playedGames < totalGames) {
      agentsReset(bot, bot2);
      setPlayedGamesWinners((prev) => [...prev, gameWinner || "Draw"]);
      setPlayedGames((prev) => prev + 1);
      startAgain();
    }
  }, [gameOver, gameWinner, playedGames, totalGames, startAgain, bot, bot2]);

  // Set win percentages whenever playedGamesWinners updates
  useEffect(() => {
    if (gameMode === "bot-vs-bot" && playedGamesWinners.length) {
      setWinPercentages(checkBotWinner(playedGamesWinners));
    }
  }, [playedGamesWinners, gameMode]);
  return {
    board,
    turn,
    lastMove,
    activeMiniBoard,
    winners,
    disabled,
    winningLine,
    agentIdTurn,
    playedGames,
    winPercentages,
    gameWinner,
    isBotThinking,
    moveNumber,
    isPaused,
    timeToMove,
    gameOver,
    handleCellClick,
    makeMove,
    togglePlayPause,
  };
};
