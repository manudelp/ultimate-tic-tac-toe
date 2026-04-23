import type { Winner, WinningLine } from "@/types/game";

type MiniBoard = string[][];
type MiniBoardWinners = Winner[][];

export const GameWinner = (
  miniBoardWinners: MiniBoardWinners,
  setWinningLine: (line: WinningLine) => void
): Winner => {
  for (let i = 0; i < 3; i++) {
    if (
      miniBoardWinners[i][0] === miniBoardWinners[i][1] &&
      miniBoardWinners[i][1] === miniBoardWinners[i][2] &&
      miniBoardWinners[i][0] !== null &&
      miniBoardWinners[i][0] !== "Draw"
    ) {
      setWinningLine({ type: "row", index: i });
      return miniBoardWinners[i][0];
    }
  }

  for (let i = 0; i < 3; i++) {
    if (
      miniBoardWinners[0][i] === miniBoardWinners[1][i] &&
      miniBoardWinners[1][i] === miniBoardWinners[2][i] &&
      miniBoardWinners[0][i] !== null &&
      miniBoardWinners[0][i] !== "Draw"
    ) {
      setWinningLine({ type: "col", index: i });
      return miniBoardWinners[0][i];
    }
  }

  if (
    miniBoardWinners[0][0] === miniBoardWinners[1][1] &&
    miniBoardWinners[1][1] === miniBoardWinners[2][2] &&
    miniBoardWinners[0][0] !== null &&
    miniBoardWinners[0][0] !== "Draw"
  ) {
    setWinningLine({ type: "diag", index: 0 });
    return miniBoardWinners[0][0];
  }

  if (
    miniBoardWinners[0][2] === miniBoardWinners[1][1] &&
    miniBoardWinners[1][1] === miniBoardWinners[2][0] &&
    miniBoardWinners[0][2] !== null &&
    miniBoardWinners[0][2] !== "Draw"
  ) {
    setWinningLine({ type: "diag", index: 1 });
    return miniBoardWinners[0][2];
  }

  if (miniBoardWinners.flat().every((winner) => winner !== null)) {
    return "Draw";
  }

  return null;
};

export const MiniBoardWinner = (miniBoard: MiniBoard): Winner => {
  if (
    !miniBoard ||
    miniBoard.length !== 3 ||
    miniBoard.some((row) => row.length !== 3)
  ) {
    return null;
  }

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

  if (miniBoard.flat().every((cell) => cell !== "")) {
    return "Draw";
  }

  return null;
};

export const convertBoardToNumeric = (
  board: string[][][][]
): number[][][][] => {
  return board.map((miniBoardRow) =>
    miniBoardRow.map((miniBoard) =>
      miniBoard.map((row) =>
        row.map((cell) => {
          if (cell === "X") return -1;
          if (cell === "O") return 1;
          return 0;
        })
      )
    )
  );
};
