export interface GameState {
  id: string;
  board: number[][][][];       // 3x3x3x3, values: 0, 1 (X), -1 (O)
  activePlayer: "X" | "O";
  forcedBoard: [number, number] | null;
  status: "ongoing" | "won" | "draw";
  winner: "X" | "O" | null;
  moves: GameMove[];
  clocks: { X: number | null; O: number | null };
  clockRunning: boolean;       // false while paused, e.g. opponent disconnected
  boardResults: number[][];    // 3x3, values: 0, 1, -1
  serverTime: number;          // unix timestamp when state was serialized
}

export interface GameMove {
  player: "X" | "O";
  move: [number, number, number, number];
  time: number;
}

export interface BotDifficulty {
  rating: number | null;       // Elo scale from bot-vs-bot games; random play is 500
  level: number | null;        // 1..maxLevel, null when unrated
  label: string;
  maxLevel: number;
}

export interface BotInfo {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: BotDifficulty;
}

export interface GameStartedEvent {
  gameId: string;
  yourPlayer: "X" | "O";
  state: GameState;
  opponent?: { type: "bot"; name: string; icon: string };
  local?: boolean;
}
