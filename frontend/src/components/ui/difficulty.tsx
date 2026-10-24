import type { BotDifficulty } from "@/types/game";

const LEVEL_COLOR = [
  "bg-emerald-500",
  "bg-lime-500",
  "bg-amber-500",
  "bg-orange-500",
  "bg-red-500",
];

const LEVEL_TEXT = [
  "text-emerald-500",
  "text-lime-500",
  "text-amber-500",
  "text-orange-500",
  "text-red-500",
];

export function DifficultyBar({ difficulty, className = "" }: { difficulty: BotDifficulty; className?: string }) {
  const { level, maxLevel } = difficulty;
  const color = level ? LEVEL_COLOR[level - 1] : "";
  return (
    <div className={`flex gap-0.5 ${className}`} aria-hidden>
      {Array.from({ length: maxLevel }, (_, i) => (
        <span key={i} className={`h-1 w-3 rounded-full ${level && i < level ? color : "bg-border"}`} />
      ))}
    </div>
  );
}

export function DifficultyLabel({ difficulty }: { difficulty: BotDifficulty }) {
  const { level, label } = difficulty;
  return (
    <span className={`text-[11px] font-medium ${level ? LEVEL_TEXT[level - 1] : "text-muted-foreground"}`}>
      {label}
    </span>
  );
}
