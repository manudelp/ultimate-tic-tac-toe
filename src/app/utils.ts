type Winner = 'X' | 'O' | 'Draw' | null;
type MiniBoardWinners = Winner[][];
type WinningLine = { type: 'row' | 'col' | 'diag'; index: number };

export const GameWinner = (
    miniBoardWinners: MiniBoardWinners,
    setWinningLine: (line: WinningLine) => void
): Winner => {
    // Check rows for a winner
    for (let i = 0; i < 3; i++) {
        if (
            miniBoardWinners[i][0] === miniBoardWinners[i][1] &&
            miniBoardWinners[i][1] === miniBoardWinners[i][2] &&
            miniBoardWinners[i][0] !== null &&
            miniBoardWinners[i][0] !== 'Draw'
        ) {
            setWinningLine({ type: 'row', index: i });
            return miniBoardWinners[i][0]; // Return the winner ('X' or 'O')
        }
    }

    // Check columns for a winner
    for (let i = 0; i < 3; i++) {
        if (
            miniBoardWinners[0][i] === miniBoardWinners[1][i] &&
            miniBoardWinners[1][i] === miniBoardWinners[2][i] &&
            miniBoardWinners[0][i] !== null &&
            miniBoardWinners[0][i] !== 'Draw'
        ) {
            setWinningLine({ type: 'col', index: i });
            return miniBoardWinners[0][i]; // Return the winner ('X' or 'O')
        }
    }

    // Check diagonal (top-left to bottom-right)
    if (
        miniBoardWinners[0][0] === miniBoardWinners[1][1] &&
        miniBoardWinners[1][1] === miniBoardWinners[2][2] &&
        miniBoardWinners[0][0] !== null &&
        miniBoardWinners[0][0] !== 'Draw'
    ) {
        setWinningLine({ type: 'diag', index: 0 });
        return miniBoardWinners[0][0]; // Return the winner ('X' or 'O')
    }

    // Check diagonal (top-right to bottom-left)
    if (
        miniBoardWinners[0][2] === miniBoardWinners[1][1] &&
        miniBoardWinners[1][1] === miniBoardWinners[2][0] &&
        miniBoardWinners[0][2] !== null &&
        miniBoardWinners[0][2] !== 'Draw'
    ) {
        setWinningLine({ type: 'diag', index: 1 });
        return miniBoardWinners[0][2]; // Return the winner ('X' or 'O')
    }

    // Check for a draw
    if (miniBoardWinners.flat().every((winner) => winner !== null)) {
        return 'Draw';
    }

    // No winner yet
    return null;
};

type MiniBoard = string[][];

export const MiniBoardWinner = (miniBoard: MiniBoard): Winner => {
    for (let i = 0; i < 3; i++) {
        if (
            miniBoard[i][0] === miniBoard[i][1] &&
            miniBoard[i][1] === miniBoard[i][2] &&
            miniBoard[i][0] !== ""
        ) {
            return miniBoard[i][0] as Winner;
        }
        if (
            miniBoard[0][i] === miniBoard[1][i] &&
            miniBoard[1][i] === miniBoard[2][i] &&
            miniBoard[0][i] !== ""
        ) {
            return miniBoard[0][i] as Winner;
        }
    }
    if (
        miniBoard[0][0] === miniBoard[1][1] &&
        miniBoard[1][1] === miniBoard[2][2] &&
        miniBoard[0][0] !== ""
    ) {
        return miniBoard[0][0] as Winner;
    }
    if (
        miniBoard[0][2] === miniBoard[1][1] &&
        miniBoard[1][1] === miniBoard[2][0] &&
        miniBoard[0][2] !== ""
    ) {
        return miniBoard[0][2] as Winner;
    }
    return null;
};

type Board = string[][][];
type MiniBoardDisabled = boolean[][];

export const NextActiveMiniBoard = (
    board: Board,
    miniBoardWinners: MiniBoardWinners,
    miniBoardDisabled: MiniBoardDisabled,
    row: number,
    col: number
): [number, number] | null => {
    if (
        miniBoardDisabled[row][col] ||
        miniBoardWinners[row][col] ||
        MiniBoardWinner([board[row][col]])
    ) {
        return null;
    } else {
        return [row, col];
    }
};

export const convertBoardToNumeric = (board: string[][][][]): number[][][][] => {
    return board.map((miniBoardRow) =>
        miniBoardRow.map((miniBoard) =>
            miniBoard.map((row) =>
                row.map((cell) => {
                    if (cell === "X") return -1; // Convert "X" to -1
                    if (cell === "O") return 1; // Convert "O" to 1
                    return 0; // Convert empty cell to 0
                })
            )
        )
    );
};

export const checkBotWinner = (winners: Winner[]): [number, number, number] => {
    const winnerCount = { X: 0, O: 0, Draw: 0 };

    winners.forEach((winner) => {
        if (winner && winner in winnerCount) {
            winnerCount[winner]++;
        }
    });

    const totalGames = winners.length;
    const winPercentages = {
        X: ((winnerCount.X / totalGames) * 100).toFixed(2),
        O: ((winnerCount.O / totalGames) * 100).toFixed(2),
        Draw: ((winnerCount.Draw / totalGames) * 100).toFixed(2),
    };

    return [
        Number(winPercentages.X),
        Number(winPercentages.O),
        Number(winPercentages.Draw),
    ];
};