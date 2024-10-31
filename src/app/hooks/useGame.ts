import { useState, useEffect, useCallback } from "react";
import { fetchBotNames, getBotMove, agentsReset } from "@/api";
import {

MiniBoardWinner,
GameWinner,
NextActiveMiniBoard,
convertBoardToNumeric,
checkBotWinner,
} from "../utils";

export const useGame = (gameMode: string, starts: string, botMatch: number, resetBoard: boolean) => {
// Board information
const [board, setBoard] = useState<string[][][][]>(
    Array.from({ length: 3 }, () =>
        Array.from({ length: 3 }, () =>
            Array.from({ length: 3 }, () => ["", "", ""])
        )
    )
);
const [turn, setTurn] = useState("X");
const [lastMove, setLastMove] = useState<[number, number, number, number] | null>(null);
const [gameWinner, setGameWinner] = useState<"X" | "O" | "Draw" | null>(null);
const [gameOver, setGameOver] = useState(false);
const [winningLine, setWinningLine] = useState<{ type: string; index: number } | null>(null);

// Mini-board information
const [activeMiniBoard, setActiveMiniBoard] = useState<[number, number]| null>(null);
const [winners, setWinners] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(null))
);
const [disabled, setDisabled] = useState(
    Array.from({ length: 3 }, () => Array(3).fill(false))
);

// Bot information
const [agentId, setAgentId] = useState<string | null>(null);
const [agentId2, setAgentId2] = useState<string | null>(null);
const [agentIdTurn, setAgentIdTurn] = useState<"X" | "O" | null>(null);
const [agentId2Turn, setAgentId2Turn] = useState<"X" | "O" | null>(null);
const [isBotThinking, setIsBotThinking] = useState(false);
const [turnsInverted, setTurnsInverted] = useState(false);
const [playedGames, setPlayedGames] = useState(0);
const [playedGamesWinners, setPlayedGamesWinners] = useState<("X" | "O" | "Draw")[]>([]);
const [winPercentages, setWinPercentages] = useState<number[]>([]);
const TIMEOUT = 0; // TODO: TIMEOUT (replace the "0" [in milliseconds])

const updateMiniBoardState = useCallback((a: number, b: number, winner: "X" | "O" | "Draw") => {
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
}, []);

const disableFullMiniBoard = useCallback(
    (a: number, b:number) => {
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
        const overallWinner = GameWinner([...prev], (line) => setWinningLine(line));
        if (overallWinner) {
            setGameWinner(overallWinner as "X" | "O" | "Draw");
            setGameOver(true);
            setDisabled(Array.from({ length: 3 }, () => Array(3).fill(true)));
        }
        return prev;
    });
}, []);

const makeMove = useCallback(
    (coords: ((prevState: null) => null) | [number, number, number, number] | null) => {
        if (!Array.isArray(coords)) {
            console.log("Invalid move");
            return;
        }
        const [a, b, c, d] = coords;
        if (gameWinner || gameOver || disabled[a][b] || board[a][b][c][d]) {
            console.log("Invalid move");
            return;
        }

        const updatedBoard = [...board];
        updatedBoard[a][b][c][d] = turn;
        setBoard(updatedBoard);

        // Check if mini-board is won
        const winner = MiniBoardWinner(updatedBoard[a][b]) as "X" | "O" | "Draw";
        if (winner) {
            updateMiniBoardState(a, b, winner);
        }

        // Check if mini-board is full
        if (updatedBoard[a][b].flat().every((cell) => cell !== "")) {
            disableFullMiniBoard(a, b);
        }

        // Check if overall game is won
        checkOverallGameWinner();

        // Set active mini-board
        setActiveMiniBoard(
            (NextActiveMiniBoard(updatedBoard as unknown as string[][][], winners, disabled, c, d) as [number, number]) || null
        );        

        // Set last move
        setLastMove(coords);

        // Set next turn
        setTurn((prev) => (prev === "X" ? "O" : "X"));
    },
    [
        gameWinner,
        gameOver,
        disabled,
        board,
        turn,
        checkOverallGameWinner,
        winners,
        updateMiniBoardState,
        disableFullMiniBoard,
    ]
);

const handleCellClick = (a: number, b: number, c: number, d: number) => {
    const coords: [number, number, number, number] = [a, b, c, d];
    if (!isBotThinking) {
        makeMove(coords);
    } else {
        alert("Let " + agentId + " cook.");
    }
};

const handleBotMove = useCallback(async () => {
    try {
        setIsBotThinking(true);
        const numericBoard: number[][][][] = convertBoardToNumeric(board);
        const coords: [number, number, number, number] = await getBotMove(numericBoard, activeMiniBoard, turn);
        makeMove(coords);
        setIsBotThinking(false);
    } catch (error) {
        setIsBotThinking(true);
        console.error("Error fetching bot's move:", error);
    }
}, [turn, board, activeMiniBoard, makeMove]);

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
    if (starts === "bot" && turn === "X") {
        invertTurns();
    }

    if (gameMode === "player-vs-bot" && turn === "O" && !gameOver) {
        handleBotMove();
    }
}, [gameMode, gameOver, turn, handleBotMove, starts, invertTurns]);

// Bot-vs-Bot
useEffect(() => {
    if (
        gameMode === "bot-vs-bot" &&
        !gameOver &&
        !isBotThinking &&
        !gameWinner &&
        playedGames < botMatch
    ) {
        // Alternate turns between agents
        if (!turnsInverted) {
            invertTurns();
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
    botMatch,
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
    if (gameOver && playedGames < botMatch) {
        agentsReset();
        setPlayedGamesWinners((prev) => [...prev, gameWinner || "Draw"]);
        startAgain();
        setPlayedGames((prev) => prev + 1);
    }
}, [gameOver, gameWinner, playedGames, botMatch, startAgain]);

// Set win percentages whenever playedGamesWinners updates
useEffect(() => {
    if (gameMode === "bot-vs-bot" && playedGamesWinners.length) {
        setWinPercentages(checkBotWinner(playedGamesWinners));
    }
}, [playedGamesWinners, gameMode]);

// Bot IDs
useEffect(() => {
    if (gameMode === "player-vs-bot") {
        fetchBotNames().then((data: string[]) => {
            setAgentId(data[0]);
            setAgentId2(null);
        });
    } else if (gameMode === "bot-vs-bot") {
        fetchBotNames().then((data: string[]) => {
            setAgentId(data[0]);
            setAgentId2(data[1]);
        });
    } else {
        setAgentId(null);
        setAgentId2(null);
    }
}, [gameMode]);

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