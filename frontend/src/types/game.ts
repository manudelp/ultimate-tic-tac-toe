export interface BotInfo {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: number;
}

export type Turn = "X" | "O";
export type Winner = "X" | "O" | "Draw" | null;
export type Coords = [number, number, number, number];
export type ActiveMiniBoard = [number, number] | null;
export type WinningLine = { type: "row" | "col" | "diag"; index: number };
export type GameMode = "player-vs-player" | "player-vs-bot" | "online";
