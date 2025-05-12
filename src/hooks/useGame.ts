import { useState, useEffect, useCallback, useRef } from "react";
import { getSocket } from "@/socket";
import { Socket } from "socket.io-client";
import { getBotMove, agentsReset } from "@/api";
import {
  MiniBoardWinner,
  GameWinner,
  convertBoardToNumeric,
} from "@/lib/utils";
import { toast } from "sonner";

interface BotListResponse {
  id: number;
  name: string;
  icon: string;
}

export const useGame = (
  gameMode: string,
  bot: BotListResponse,
  starts: string,
  yourLetter?: string,
  lobbyCode?: string
) => {
  // Socket reference
  const socketRef = useRef<Socket | null>(null);

  // Types
  type Board = string[][][][];
  type MiniBoard = string[][];
  type Turn = "X" | "O";
  type Winner = "X" | "O" | "Draw";
  type Coords = [number, number, number, number];
  type WinningLine = { type: string; index: number };
  type ActiveMiniBoard = [number, number] | null;
  type MoveHistory = { turn: Turn; coords: Coords }[];
  type MoveData = {
    bigRow: number;
    bigCol: number;
    smallRow: number;
    smallCol: number;
  };

  // Initial state
  const initialBoard = Array.from({ length: 3 }, () =>
    Array.from({ length: 3 }, () =>
      Array.from({ length: 3 }, () => ["", "", ""])
    )
  );

  const initialState = {
    board: initialBoard,
    turn: starts === "player" ? "X" : "O",
    lastMove: null,
    gameWinner: null,
    gameOver: false,
    winningLine: null,
    moveNumber: 0,
    moveHistory: [] as MoveHistory,
  };

  // Board information
  const [board, setBoard] = useState<Board>(initialBoard);
  const [turn, setTurn] = useState<Turn>("X");
  const [lastMove, setLastMove] = useState<Coords | null>(null);
  const [gameWinner, setGameWinner] = useState<Winner | null>(null);
  const [gameOver, setGameOver] = useState(false);
  const [winningLine, setWinningLine] = useState<WinningLine | null>(null);
  const [moveNumber, setMoveNumber] = useState(0);
  const [moveHistory, setMoveHistory] = useState<MoveHistory>([]);

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

  // FUNCTIONS
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
      // Get the winning line first, so we can send it immediately with the gameOver event
      let capturedWinningLine: WinningLine | null = null;

      const overallWinner = GameWinner([...prev], (line) => {
        capturedWinningLine = line;
        setWinningLine(line);
      });

      if (overallWinner) {
        setGameWinner(overallWinner as "X" | "O" | "Draw");
        setGameOver(true);

        const winnerSound = new Audio("/assets/sounds/winner_xmas.mp3");
        winnerSound.volume = 0.2;
        winnerSound.play();

        setDisabled(Array.from({ length: 3 }, () => Array(3).fill(true)));

        // Notify opponent about game over in online mode with the winning line
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

      // Early validation
      if (gameWinner || gameOver || disabled[a][b] || board[a][b][c][d]) {
        return;
      }

      // Use functional form to ensure we always have the latest board state
      setBoard((prevBoard) => {
        // Create a deep copy of the current board
        const newBoard = JSON.parse(JSON.stringify(prevBoard));

        // Update the new board - use the provided letter or current turn
        newBoard[a][b][c][d] = forcedLetter || turn;

        // Immediately check for mini-board winner
        const winner = MiniBoardWinner(newBoard[a][b] as MiniBoard);
        if (winner) {
          // Call this synchronously to update immediately
          updateMiniBoardState(a, b, winner);
        }

        // Calculate next active mini-board
        const nextMiniBoard = MiniBoardWinner(newBoard[c][d] as MiniBoard);
        if (!disabled[c][d] && !winners[c][d] && !nextMiniBoard) {
          setActiveMiniBoard([c, d]);
        } else {
          setActiveMiniBoard(null);
        }

        // Check if mini-board is full
        if (newBoard[a][b].flat().every((cell: string) => cell !== "")) {
          disableFullMiniBoard(a, b);
        }

        // Check overall game winner
        checkOverallGameWinner();

        // Return the updated board to set as new state
        return newBoard;
      });

      // Process rest of game logic in timeout to ensure board is updated first
      setTimeout(() => {
        // Play sound
        try {
          const tapSound = new Audio("/assets/sounds/tap.mp3");
          tapSound.volume = 0.25;
          tapSound.play().catch(() => {
            return;
          });
        } catch (error) {
          return error;
        }

        setLastMove(coords);
        setTurn((prev) => (prev === "X" ? "O" : "X"));
        setMoveNumber((prev) => prev + 1);
        setMoveHistory((prev) => [
          ...prev,
          { turn: forcedLetter || turn, coords },
        ]);

        if (gameMode === "online" && lobbyCode && emitMove) {
          if (socketRef.current) {
            socketRef.current.emit("makeMove", {
              code: lobbyCode,
              move: { bigRow: a, bigCol: b, smallRow: c, smallCol: d },
            });
          }
        }
      }, 0);
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
      gameMode,
      lobbyCode,
    ]
  );

  const handleCellClick = (a: number, b: number, c: number, d: number) => {
    if (gameOver) {
      return;
    }

    const coords: Coords = [a, b, c, d];

    // Check if cell is already occupied
    if (board[a][b][c][d]) {
      toast.warning("This cell is already occupied!");
      return;
    }

    // Online mode check - must come FIRST
    if (gameMode === "online" && turn !== yourLetter) {
      // Provide feedback that it's not their turn
      toast.warning("Not your turn!");
      return;
    }

    // Bot mode check
    if (gameMode === "player-vs-bot" && isBotThinking) {
      // add animation to the cell when it isn't player's turn
      toast.error("Let " + bot?.name + " " + bot?.icon + " cook.");
      return;
    }

    // If we got this far, the move is valid
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
      // If moveData is just the letter, we can't process it
      if (typeof moveData === "string") {
        console.error("Received letter instead of move data:", moveData);
        return;
      }

      // Safety check - if moveData is undefined or null, don't proceed
      if (!moveData) {
        console.error("Received invalid move data:", moveData);
        return;
      }

      // Extract move from moveData if it's nested
      let move = moveData;
      if (
        typeof moveData === "object" &&
        moveData !== null &&
        "move" in moveData
      ) {
        move = moveData.move as MoveData;
      }

      // Convert move to array format if it's an object
      let moveArray: [number, number, number, number];

      if (Array.isArray(move)) {
        // Ensure the array has all required elements
        if (move.length < 4) {
          console.error("Move array doesn't have enough elements:", move);
          return;
        }
        moveArray = [
          Number(move[0]),
          Number(move[1]),
          Number(move[2]),
          Number(move[3]),
        ];
      } else if (typeof move === "object" && move !== null) {
        // Check if object has all required properties
        if (
          move.bigRow === undefined ||
          move.bigCol === undefined ||
          move.smallRow === undefined ||
          move.smallCol === undefined
        ) {
          console.error("Move object missing required properties:", move);
          return;
        }
        moveArray = [
          Number(move.bigRow),
          Number(move.bigCol),
          Number(move.smallRow),
          Number(move.smallCol),
        ];
      } else {
        console.error("Move is neither an array nor an object:", move);
        return;
      }

      // Final validation before making move
      if (
        !moveArray.every((coord) => typeof coord === "number" && !isNaN(coord))
      ) {
        console.error("Invalid coordinates in moveArray:", moveArray);
        return;
      }

      makeMove(moveArray, opponentLetter, false);
    },
    [makeMove]
  );

  const resetGame = () => {
    setBoard(initialState.board);
    setTurn(initialState.turn as Turn);
    setLastMove(initialState.lastMove);
    setGameWinner(initialState.gameWinner);
    setGameOver(initialState.gameOver);
    setWinningLine(initialState.winningLine);
    setMoveNumber(initialState.moveNumber);
    setActiveMiniBoard(null);
    setWinners(Array.from({ length: 3 }, () => Array(3).fill(null)));
    setDisabled(Array.from({ length: 3 }, () => Array(3).fill(false)));
    setIsBotThinking(false);
    setTimeToMove(0);
    setMoveHistory([]);
  };

  // Restart bot move each game
  useEffect(() => {
    if (gameMode === "player-vs-bot" && !lastMove) {
      agentsReset(bot.id);
    }
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
      setIsBotThinking(true);
      handleBotMove();
    }
  }, [turn, starts, gameMode, handleBotMove, gameOver, isBotThinking]);

  // Online mode - handle socket events
  useEffect(() => {
    if (gameMode === "online") {
      // Initialize socket only when in online mode
      socketRef.current = getSocket();
      const socket = socketRef.current;
      const opponentLetter = yourLetter === "X" ? "O" : "X";

      socket.on("opponentMove", (move) => {
        handleOpponentMove(move, opponentLetter);
      });

      // Add opponent left listener
      socket.on("opponentLeft", () => {
        toast.error("Your opponent has left the game", {
          duration: 3000,
        });
        // Automatically exit to home page after a delay
        setTimeout(() => {
          window.location.href = "/";
        }, 3000);
      });

      return () => {
        socket.off("opponentMove");
        socket.off("gameOver");
        socket.off("opponentLeft");
      };
    }
  }, [gameMode, handleOpponentMove, yourLetter]);

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
    moveHistory,
    handleCellClick,
    makeMove,
    resetGame,
  };
};
