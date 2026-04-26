export interface GameState {
  id: string;
  board: number[][][][];       // 3x3x3x3, values: 0, 1 (X), -1 (O)
  activePlayer: "X" | "O";
  forcedBoard: [number, number] | null;
  status: "ongoing" | "won" | "draw";
  winner: "X" | "O" | null;
  moves: GameMove[];
  clocks: { X: number | null; O: number | null };
  boardResults: number[][];    // 3x3, values: 0, 1, -1
}

export interface GameMove {
  player: "X" | "O";
  move: [number, number, number, number];
  time: number;
}

export interface BotInfo {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: number;
}

export interface GameStartedEvent {
  gameId: string;
  yourPlayer: "X" | "O";
  state: GameState;
  opponent?: { type: "bot"; name: string; icon: string };
  local?: boolean;
}
