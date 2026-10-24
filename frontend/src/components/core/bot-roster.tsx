"use client";

import { useEffect, useState } from "react";
import { getBots } from "@/api";
import type { BotInfo } from "@/types/game";
import { DifficultyBar, DifficultyLabel } from "@/components/ui/difficulty";

// How each bot plays, for players learning the game. Keyed by bot id.
const HOW_IT_PLAYS: Record<number, string> = {
  0: "Plays completely randomly. Good for learning the basic flow of the game without any pressure.",
  1: "Takes a mini-board the moment it can and otherwise picks what looks best right now. Predictable, but it punishes loose moves.",
  3: "Searches several moves ahead with alpha-beta pruning and a positional evaluation. A genuine challenge for experienced players.",
  4: "Runs Arkadiusz Nowaczyński's NMCTS2 network, the engine behind uttt.ai, with a thousand simulations a move. The strongest opponent here.",
};

export default function BotRoster() {
  const [bots, setBots] = useState<BotInfo[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getBots().then(setBots).catch(() => setFailed(true));
  }, []);

  if (failed) {
    return <p className="text-sm text-muted-foreground">The AI opponents could not be loaded right now.</p>;
  }

  if (!bots) {
    return (
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-[76px] rounded-xl border border-border/50 bg-surface/40 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {bots.map((bot) => (
        <div key={bot.id} className="flex gap-4 p-4 rounded-xl border border-border/50 bg-background">
          <span className="text-2xl leading-none shrink-0 mt-0.5">{bot.icon}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <p className="text-sm font-semibold">{bot.name}</p>
              <DifficultyBar difficulty={bot.difficulty} />
              <DifficultyLabel difficulty={bot.difficulty} />
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">{HOW_IT_PLAYS[bot.id] ?? bot.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
