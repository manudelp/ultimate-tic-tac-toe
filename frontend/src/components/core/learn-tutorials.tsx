"use client";
import { useState } from "react";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";

// ── Tiny board renderer ────────────────────────────────────
type Mark = "X" | "O" | "";

function MiniCell({ mark, highlight, active, onClick }: {
  mark: Mark; highlight?: boolean; active?: boolean; onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`aspect-square rounded-sm flex items-center justify-center transition-colors duration-150 ${
        onClick ? "cursor-pointer" : ""
      } ${
        highlight ? "bg-green-500/30" :
        active && !mark ? "bg-[hsl(var(--board-cell))] hover:bg-[hsl(var(--board-cell-hover))]" :
        "bg-[hsl(var(--board-cell))]"
      }`}
    >
      {mark && (
        <svg viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round" className={`w-[65%] h-[65%] ${mark === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"}`}>
          {mark === "X" ? (<><path d="M18 6l-12 12"/><path d="M6 6l12 12"/></>) : <circle cx="12" cy="12" r="7.5"/>}
        </svg>
      )}
    </div>
  );
}

function SmallBoard({ cells, active, winner, highlight, onCell }: {
  cells: Mark[]; active?: boolean; winner?: Mark | "draw" | null;
  highlight?: boolean; onCell?: (i: number) => void;
}) {
  const ring = active ? "ring-2 ring-blue-500/50 bg-blue-500/10" : "bg-[hsl(var(--board-bg))]";
  return (
    <div className={`relative rounded-md p-0.5 transition-colors ${ring} ${highlight ? "ring-2 ring-green-500/60 bg-green-500/10" : ""}`}>
      <div className={`grid grid-cols-3 gap-px ${winner ? "opacity-0" : ""}`}>
        {cells.map((m, i) => (
          <MiniCell key={i} mark={m} active={active && !winner} onClick={active && !m && onCell ? () => onCell(i) : undefined} />
        ))}
      </div>
      {winner && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          {winner === "draw" ? (
            <svg viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" className="w-3/5 h-3/5 text-muted-foreground"><path d="M5 12h14"/></svg>
          ) : (
            <svg viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round" className={`w-3/5 h-3/5 ${winner === "X" ? "text-[hsl(var(--markx))]" : "text-[hsl(var(--marko))]"}`}>
              {winner === "X" ? (<><path d="M18 6l-12 12"/><path d="M6 6l12 12"/></>) : <circle cx="12" cy="12" r="7.5"/>}
            </svg>
          )}
        </div>
      )}
    </div>
  );
}

function checkWinner(cells: Mark[]): Mark | "draw" | null {
  const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  for (const [a,b,c] of lines) {
    if (cells[a] && cells[a] === cells[b] && cells[b] === cells[c]) return cells[a] as Mark;
  }
  if (cells.every(c => c)) return "draw";
  return null;
}

// ── Tutorial 1: The Forced Move ────────────────────────────
export function ForcedMoveTutorial() {
  const STEPS = [
    {
      label: "X plays in the center cell of the center board.",
      desc: "X picks cell 4 (center) of board [1,1]. That cell position (4 = center) means O must now play in board [1,1]... wait — that's the same board. Let's use a clearer example.",
      board: 4, // which big board is active (0-8)
      cells: Array(9).fill("") as Mark[],
      nextBoard: 4,
      highlight: [4],
      move: 4,
      player: "X" as Mark,
    },
  ];

  // Hardcoded 3-step scenario
  // Big board index: 0=TL,1=TC,2=TR,3=ML,4=MC,5=MR,6=BL,7=BC,8=BR
  // Step 1: X plays cell 2 (top-right) of board 4 (center) → O must play board 2 (top-right)
  // Step 2: O plays cell 6 (bottom-left) of board 2 → X must play board 6 (bottom-left)
  // Step 3: X plays cell 1 (top-center) of board 6 → O must play board 1 (top-center)

  type Step = {
    instruction: string;
    detail: string;
    activeBoard: number;
    boards: (Mark[])[]; // 9 boards × 9 cells
    highlightBoard?: number;
    highlightCell?: number;
    player: Mark;
    done?: boolean;
  };

  const emptyBoards = (): Mark[][] => Array(9).fill(null).map(() => Array(9).fill("") as Mark[]);

  const b0 = emptyBoards();
  const b1 = emptyBoards();
  b1[4][2] = "X";
  const b2 = emptyBoards();
  b2[4][2] = "X";
  b2[2][6] = "O";
  const b3 = emptyBoards();
  b3[4][2] = "X";
  b3[2][6] = "O";
  b3[6][1] = "X";

  const steps: Step[] = [
    {
      instruction: "X plays in the top-right cell of the center board.",
      detail: "Cell position top-right = index 2. So O is forced to play in board 2 — the top-right board.",
      activeBoard: 4,
      boards: b0,
      highlightBoard: 2,
      player: "X",
    },
    {
      instruction: "O is forced into the top-right board. O plays bottom-left.",
      detail: "O picks cell 6 (bottom-left) of board 2. That sends X to board 6 — the bottom-left board.",
      activeBoard: 2,
      boards: b1,
      highlightBoard: 6,
      player: "O",
    },
    {
      instruction: "X is forced into the bottom-left board. X plays top-center.",
      detail: "X picks cell 1 (top-center) of board 6. That sends O to board 1 — the top-center board.",
      activeBoard: 6,
      boards: b2,
      highlightBoard: 1,
      player: "X",
    },
    {
      instruction: "O is forced into the top-center board.",
      detail: "Every move sends the opponent to a specific board. This chain of forced moves is the core mechanic of Ultimate Tic-Tac-Toe.",
      activeBoard: 1,
      boards: b3,
      player: "O",
      done: true,
    },
  ];

  const [step, setStep] = useState(0);
  const s = steps[step];

  const POSITIONS = ["TL","TC","TR","ML","MC","MR","BL","BC","BR"];

  return (
    <div className="rounded-xl border border-border/50 bg-background overflow-hidden">
      <div className="p-4 border-b border-border/50 flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">{s.instruction}</p>
          <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{s.detail}</p>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {steps.map((_, i) => (
            <div key={i} className={`w-1.5 h-1.5 rounded-full transition-colors ${i === step ? "bg-blue-400" : "bg-border"}`} />
          ))}
        </div>
      </div>

      <div className="p-4 flex flex-col sm:flex-row gap-6 items-center">
        {/* Big board */}
        <div className="grid grid-cols-3 gap-1.5 w-[220px] shrink-0">
          {s.boards.map((cells, bi) => {
            const isActive = bi === s.activeBoard;
            const isHighlight = bi === s.highlightBoard;
            return (
              <SmallBoard
                key={bi}
                cells={cells}
                active={isActive}
                highlight={isHighlight}
              />
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex flex-col gap-3 text-sm flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm bg-blue-500/20 ring-2 ring-blue-500/50 shrink-0" />
            <span className="text-muted-foreground text-xs">Active board — must play here</span>
          </div>
          {s.highlightBoard !== undefined && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-sm bg-green-500/20 ring-2 ring-green-500/60 shrink-0" />
              <span className="text-muted-foreground text-xs">
                Next forced board ({POSITIONS[s.highlightBoard]})
              </span>
            </div>
          )}
          {s.done && (
            <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
              <p className="text-xs text-green-400 font-medium">Key insight</p>
              <p className="text-xs text-muted-foreground mt-1">Your move doesn&apos;t just place a mark — it controls where your opponent plays next.</p>
            </div>
          )}
        </div>
      </div>

      <div className="px-4 pb-4 flex justify-between">
        <button
          onClick={() => setStep(s => Math.max(0, s - 1))}
          disabled={step === 0}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-surface hover:bg-surface-hover disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-3.5 h-3.5" /> Previous
        </button>
        <button
          onClick={() => setStep(s => Math.min(steps.length - 1, s + 1))}
          disabled={step === steps.length - 1}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-surface hover:bg-surface-hover disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          Next <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

// ── Tutorial 2: Free Choice (sent to won/full board) ───────
export function FreeChoiceTutorial() {
  const wonCells: Mark[] = ["X","O","X","O","X","O","X","","X"];
  // board 4 is won by X
  const boards = Array(9).fill(null).map(() => Array(9).fill("") as Mark[]);
  boards[4] = ["X","O","X","X","O","O","O","X","X"];

  const [chosen, setChosen] = useState<number | null>(null);

  return (
    <div className="rounded-xl border border-border/50 bg-background overflow-hidden">
      <div className="p-4 border-b border-border/50">
        <p className="text-sm font-semibold">O is sent to the center board — but it&apos;s already won.</p>
        <p className="text-xs text-muted-foreground mt-0.5">When the forced board is unavailable, O can play in <span className="text-foreground font-medium">any open board</span>. Click one to choose.</p>
      </div>
      <div className="p-4 flex flex-col sm:flex-row gap-6 items-center">
        <div className="grid grid-cols-3 gap-1.5 w-[220px] shrink-0">
          {boards.map((cells, bi) => {
            const isWon = bi === 4;
            const isChosen = bi === chosen;
            return (
              <div
                key={bi}
                onClick={() => !isWon && setChosen(bi)}
                className={`relative rounded-md p-0.5 transition-colors cursor-pointer ${
                  isWon ? "bg-[hsl(var(--board-bg))] cursor-default" :
                  isChosen ? "ring-2 ring-red-500/50 bg-red-500/10" :
                  "bg-[hsl(var(--board-bg))] hover:ring-2 hover:ring-red-500/30 hover:bg-red-500/5"
                }`}
              >
                <div className={`grid grid-cols-3 gap-px ${isWon ? "opacity-0" : ""}`}>
                  {cells.map((m, i) => <MiniCell key={i} mark={m} />)}
                </div>
                {isWon && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <svg viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round" className="w-3/5 h-3/5 text-[hsl(var(--markx))]">
                      <path d="M18 6l-12 12"/><path d="M6 6l12 12"/>
                    </svg>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div className="flex flex-col gap-3 flex-1 min-w-0">
          {chosen === null ? (
            <p className="text-xs text-muted-foreground">Click any open board to play there.</p>
          ) : (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
              <p className="text-xs text-red-400 font-medium">Board {["TL","TC","TR","ML","MC","MR","BL","BC","BR"][chosen]} selected</p>
              <p className="text-xs text-muted-foreground mt-1">O can play anywhere in this board. The move O makes will then determine where X must go next.</p>
            </div>
          )}
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm bg-[hsl(var(--board-bg))] ring-1 ring-border shrink-0" />
            <span className="text-xs text-muted-foreground">Won board — unavailable</span>
          </div>
        </div>
      </div>
      {chosen !== null && (
        <div className="px-4 pb-4">
          <button onClick={() => setChosen(null)} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
            <RotateCcw className="w-3 h-3" /> Reset
          </button>
        </div>
      )}
    </div>
  );
}

// ── Tutorial 3: Win a mini-board ───────────────────────────
export function WinMiniBoardTutorial() {
  const initial: Mark[] = ["X","O","","X","O","","","",""];
  const [cells, setCells] = useState<Mark[]>(initial);
  const [player, setPlayer] = useState<Mark>("X");
  const winner = checkWinner(cells);

  const handleClick = (i: number) => {
    if (cells[i] || winner) return;
    const next = [...cells];
    next[i] = player;
    setCells(next);
    setPlayer(p => p === "X" ? "O" : "X");
  };

  const reset = () => { setCells(initial); setPlayer("X"); };

  return (
    <div className="rounded-xl border border-border/50 bg-background overflow-hidden">
      <div className="p-4 border-b border-border/50">
        <p className="text-sm font-semibold">
          {winner ? (winner === "draw" ? "Draw!" : `${winner} wins this mini-board!`) : `${player}'s turn — complete the win.`}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">
          {winner ? "Winning a mini-board claims that cell on the big board." : "X needs one more move to win. Click the right cell."}
        </p>
      </div>
      <div className="p-4 flex flex-col sm:flex-row gap-6 items-center">
        <div className="w-[140px] shrink-0">
          <SmallBoard cells={cells} active={!winner} winner={winner} onCell={handleClick} />
        </div>
        <div className="flex flex-col gap-2 flex-1 min-w-0">
          {!winner ? (
            <p className="text-xs text-muted-foreground">X has two in a column on the left. One more and X claims this board.</p>
          ) : winner !== "draw" ? (
            <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
              <p className="text-xs text-green-400 font-medium">Mini-board won!</p>
              <p className="text-xs text-muted-foreground mt-1">On the big board, this cell now shows {winner}&apos;s mark. Three of these in a row wins the game.</p>
            </div>
          ) : null}
          <button onClick={reset} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors w-fit">
            <RotateCcw className="w-3 h-3" /> Reset
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Tutorial 4: Strategy — sending to bad boards ───────────
export function StrategyTutorial() {
  const STEPS = [
    {
      title: "X is about to win board 7 (bottom-center).",
      desc: "X can play cell 7 in board 7 to win it. But where does that send O?",
      activeBoard: 7,
      boards: (() => {
        const b = Array(9).fill(null).map(() => Array(9).fill("") as Mark[]);
        b[7] = ["X","O","","","X","O","","",""] as Mark[];
        return b;
      })(),
      highlight: 7,
    },
    {
      title: "Playing cell 7 sends O to board 7 — but it's now won.",
      desc: "O gets a free choice! That's bad for X. Think about where your move sends the opponent before committing.",
      activeBoard: 7,
      boards: (() => {
        const b = Array(9).fill(null).map(() => Array(9).fill("") as Mark[]);
        b[7] = ["X","O","","","X","O","","X",""] as Mark[];
        return b;
      })(),
      highlight: 7,
      freeChoice: true,
    },
    {
      title: "Better: win board 7 via cell 4 instead.",
      desc: "Cell 4 also wins board 7 (diagonal), but sends O to board 4 — the center, which X is already contesting. That's a much worse position for O.",
      activeBoard: 7,
      boards: (() => {
        const b = Array(9).fill(null).map(() => Array(9).fill("") as Mark[]);
        b[7] = ["X","O","","","X","O","","",""] as Mark[];
        b[4] = ["X","","","","","","","",""] as Mark[];
        return b;
      })(),
      highlight: 4,
      good: true,
    },
  ];

  const [step, setStep] = useState(0);
  const s = STEPS[step];

  return (
    <div className="rounded-xl border border-border/50 bg-background overflow-hidden">
      <div className="p-4 border-b border-border/50 flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">{s.title}</p>
          <p className={`text-xs mt-0.5 leading-relaxed ${s.freeChoice ? "text-red-400" : s.good ? "text-green-400" : "text-muted-foreground"}`}>{s.desc}</p>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {STEPS.map((_, i) => (
            <div key={i} className={`w-1.5 h-1.5 rounded-full transition-colors ${i === step ? "bg-blue-400" : "bg-border"}`} />
          ))}
        </div>
      </div>
      <div className="p-4">
        <div className="grid grid-cols-3 gap-1.5 w-[220px]">
          {s.boards.map((cells, bi) => (
            <SmallBoard key={bi} cells={cells} active={bi === s.activeBoard} highlight={bi === s.highlight} />
          ))}
        </div>
      </div>
      <div className="px-4 pb-4 flex justify-between">
        <button onClick={() => setStep(s => Math.max(0, s - 1))} disabled={step === 0} className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-surface hover:bg-surface-hover disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
          <ChevronLeft className="w-3.5 h-3.5" /> Previous
        </button>
        <button onClick={() => setStep(s => Math.min(STEPS.length - 1, s + 1))} disabled={step === STEPS.length - 1} className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-surface hover:bg-surface-hover disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
          Next <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
