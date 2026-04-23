import type { Coords } from "@/types/game";

const BOARD_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];
const CELL_LABELS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"];

export function formatMove(coords: Coords): string {
  const boardIndex = coords[0] * 3 + coords[1];
  const cellIndex = coords[2] * 3 + coords[3];
  return `${BOARD_LABELS[boardIndex]}${CELL_LABELS[cellIndex]}`;
}
