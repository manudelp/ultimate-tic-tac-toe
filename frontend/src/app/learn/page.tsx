import Link from "next/link";
import { Target, BookOpen, Trophy, Lightbulb, Zap, ArrowRight, Info, MousePointer, AlertTriangle, HelpCircle, Cpu } from "lucide-react";
import { ForcedMoveTutorial, FreeChoiceTutorial, WinMiniBoardTutorial, StrategyTutorial } from "@/components/core/learn-tutorials";
import SectionNav from "@/components/ui/section-nav";

const SECTIONS = [
  { id: "objective",  title: "Objective",       icon: "Target" },
  { id: "rules",      title: "Rules",            icon: "BookOpen" },
  { id: "tutorial",   title: "Tutorials",        icon: "MousePointer" },
  { id: "winning",    title: "Winning",          icon: "Trophy" },
  { id: "strategies", title: "Strategies",       icon: "Lightbulb" },
  { id: "mistakes",   title: "Mistakes",         icon: "AlertTriangle" },
  { id: "bots",       title: "AI Opponents",     icon: "Cpu" },
  { id: "faq",        title: "FAQ",              icon: "HelpCircle" },
  { id: "tips",       title: "Tips",             icon: "Zap" },
];

export default function Learn() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-8 py-12">

      {/* Header */}
      <div className="mb-12">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Guide</p>
        <h1 className="text-4xl font-bold mb-3">How to Play</h1>
        <p className="text-muted-foreground text-base leading-relaxed max-w-xl">
          Ultimate Tic-Tac-Toe looks simple but rewards deep thinking. Learn the rules, play through the tutorials, then master the strategy.
        </p>
      </div>

      <div className="flex flex-col md:flex-row md:gap-12">

        <SectionNav sections={SECTIONS} />

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-16">

          {/* ── Objective ── */}
          <section id="objective" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                <Target className="w-4 h-4 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">Objective</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Ultimate Tic-Tac-Toe is played on a 3×3 grid of smaller Tic-Tac-Toe boards — nine boards in total.
              Win three small boards in a row (horizontally, vertically, or diagonally) to win the game.
            </p>
            <div className="flex gap-3 p-4 rounded-xl border border-blue-500/20 bg-blue-500/5 mb-4">
              <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground leading-relaxed">
                Think of it as regular Tic-Tac-Toe, but each cell <em>is</em> its own Tic-Tac-Toe game.
                Win the small game to claim that cell on the big board.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { label: "9 mini-boards", desc: "Arranged in a 3×3 grid, each fully playable." },
                { label: "81 cells total", desc: "9 cells per mini-board × 9 boards." },
                { label: "2 players", desc: "X always goes first in a new game." },
              ].map(({ label, desc }) => (
                <div key={label} className="p-3 rounded-xl border border-border/50 bg-background text-center">
                  <p className="text-sm font-bold mb-1">{label}</p>
                  <p className="text-xs text-muted-foreground">{desc}</p>
                </div>
              ))}
            </div>
          </section>

          {/* ── Rules ── */}
          <section id="rules" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center shrink-0">
                <BookOpen className="w-4 h-4 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold">Rules</h2>
            </div>
            <div className="space-y-3 mb-6">
              {[
                { n: "1", text: "Play your mark (X or O) in any empty cell of the currently active mini-board.", highlight: false },
                { n: "2", text: "The position of the cell you pick determines which mini-board your opponent must play in next. Play in the top-left cell → opponent plays in the top-left mini-board.", highlight: true },
                { n: "3", text: "If the forced board is already won or completely full, your opponent may play in any open board of their choice.", highlight: false },
                { n: "4", text: "Win a mini-board by getting three of your marks in a row within it — just like regular Tic-Tac-Toe.", highlight: false },
                { n: "5", text: "Win the game by claiming three mini-boards in a row on the big board.", highlight: false },
              ].map(({ n, text, highlight }) => (
                <div key={n} className={`flex gap-4 p-4 rounded-xl border ${highlight ? "border-purple-500/20 bg-purple-500/5" : "border-border/50 bg-background"}`}>
                  <span className={`text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${highlight ? "bg-purple-500/20 text-purple-400" : "bg-surface text-muted-foreground"}`}>{n}</span>
                  <p className="text-sm text-muted-foreground leading-relaxed">{text}</p>
                </div>
              ))}
            </div>

            {/* Board state reference */}
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Board states</p>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { color: "blue", label: "Active", desc: "Highlighted in blue (X's turn) or red (O's turn). You must play here." },
                { color: "muted", label: "Inactive", desc: "Dimmed. You cannot play here this turn — the forced board rule applies." },
                { color: "green", label: "Won / Full", desc: "Shows the winner's mark or a dash for a draw. Hover to reveal the cells inside." },
              ].map(({ color, label, desc }) => (
                <div key={label} className="p-3 rounded-xl border border-border/50 bg-background">
                  <div className="flex items-center gap-2 mb-1.5">
                    <div className={`w-2.5 h-2.5 rounded-sm ${color === "blue" ? "bg-blue-500/40 ring-1 ring-blue-500" : color === "green" ? "bg-green-500/20 ring-1 ring-green-500/50" : "bg-surface ring-1 ring-border"}`} />
                    <p className="text-xs font-semibold">{label}</p>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </section>

          {/* ── Tutorials ── */}
          <section id="tutorial" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center shrink-0">
                <MousePointer className="w-4 h-4 text-cyan-400" />
              </div>
              <h2 className="text-2xl font-bold">Interactive Tutorials</h2>
            </div>

            <div className="space-y-8">
              <div>
                <p className="text-sm font-semibold mb-1">1 — The forced move</p>
                <p className="text-xs text-muted-foreground mb-3">The most important mechanic. Step through how each move chains to the next.</p>
                <ForcedMoveTutorial />
              </div>

              <div>
                <p className="text-sm font-semibold mb-1">2 — Free choice</p>
                <p className="text-xs text-muted-foreground mb-3">When the forced board is unavailable, the player picks freely.</p>
                <FreeChoiceTutorial />
              </div>

              <div>
                <p className="text-sm font-semibold mb-1">3 — Win a mini-board</p>
                <p className="text-xs text-muted-foreground mb-3">Complete the win to claim this board on the big grid.</p>
                <WinMiniBoardTutorial />
              </div>

              <div>
                <p className="text-sm font-semibold mb-1">4 — Think before you win</p>
                <p className="text-xs text-muted-foreground mb-3">Winning a board is good — but where you win it matters just as much.</p>
                <StrategyTutorial />
              </div>
            </div>
          </section>

          {/* ── Winning ── */}
          <section id="winning" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center shrink-0">
                <Trophy className="w-4 h-4 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold">Winning</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Win three mini-boards in a row on the larger grid — horizontally, vertically, or diagonally — just like regular Tic-Tac-Toe.
              There are 8 possible winning lines on the big board.
            </p>
            <div className="grid gap-3 sm:grid-cols-2 mb-4">
              {[
                { label: "3 horizontal lines", desc: "Top row, middle row, bottom row." },
                { label: "3 vertical lines", desc: "Left column, center column, right column." },
                { label: "2 diagonal lines", desc: "Top-left to bottom-right, top-right to bottom-left." },
                { label: "Draw condition", desc: "All 9 boards are resolved with no winner on the big board." },
              ].map(({ label, desc }) => (
                <div key={label} className="flex gap-3 p-3 rounded-xl border border-border/50 bg-background">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-400 shrink-0 mt-1.5" />
                  <div>
                    <p className="text-sm font-semibold">{label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex gap-3 p-4 rounded-xl border border-green-500/20 bg-green-500/5">
              <Info className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground leading-relaxed">
                A mini-board that ends in a draw is considered neutral — it doesn&apos;t count for either player on the big board, but it <em>is</em> considered full and will trigger free choice if a player is sent there.
              </p>
            </div>
          </section>

          {/* ── Strategies ── */}
          <section id="strategies" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center shrink-0">
                <Lightbulb className="w-4 h-4 text-yellow-400" />
              </div>
              <h2 className="text-2xl font-bold">Strategies</h2>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 mb-6">
              {[
                { title: "Think two moves ahead", desc: "Always consider where your move sends your opponent, not just whether it wins the current mini-board. A winning move that gives your opponent a free choice can be a net loss." },
                { title: "Control the center board", desc: "The center mini-board (position 4) connects to the most winning lines on the big board — 4 lines pass through it. Winning it early gives a structural advantage." },
                { title: "Send them to bad boards", desc: "Force your opponent into boards where they have no good moves: already-won boards (free choice is bad for you), boards where you're already winning, or boards where they can't threaten anything." },
                { title: "Balance offense and defense", desc: "Sometimes blocking your opponent from winning a mini-board is more valuable than advancing your own position. Letting them win a board to gain a better forced position is a valid trade." },
                { title: "Corner boards are powerful", desc: "Corner boards (0, 2, 6, 8) each participate in 3 winning lines. Controlling corners gives you more paths to victory on the big board." },
                { title: "Avoid giving free choice", desc: "Sending your opponent to a won or full board gives them a free choice — they can play anywhere. This is almost always bad for you. Try to always send them to a live, contested board." },
              ].map(({ title, desc }) => (
                <div key={title} className="p-4 rounded-xl border border-border/50 bg-background">
                  <h3 className="text-sm font-semibold mb-1.5">{title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
            <div className="flex gap-3 p-4 rounded-xl border border-yellow-500/20 bg-yellow-500/5">
              <Info className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground leading-relaxed">
                The best players think of the game in two layers simultaneously: the local battle inside each mini-board, and the global battle for the big board. Sacrificing a mini-board to gain a better global position is often the right call.
              </p>
            </div>
          </section>

          {/* ── Common Mistakes ── */}
          <section id="mistakes" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-4 h-4 text-red-400" />
              </div>
              <h2 className="text-2xl font-bold">Common Mistakes</h2>
            </div>
            <div className="space-y-3">
              {[
                { mistake: "Focusing only on the current mini-board", fix: "Always check where your move sends your opponent before placing your mark. The global consequence matters more than the local win." },
                { mistake: "Winning a board without checking the destination", fix: "If winning a board sends your opponent to a free-choice situation, consider whether a different winning cell would send them somewhere worse." },
                { mistake: "Ignoring the center board", fix: "The center board is the most strategically valuable. Letting your opponent win it unchallenged is a significant disadvantage." },
                { mistake: "Playing too defensively in mini-boards", fix: "Blocking every threat inside a mini-board can waste moves. Sometimes letting your opponent win a mini-board while you gain a better global position is the right trade." },
                { mistake: "Not using the move history", fix: "After a loss, review the move history to find the exact moment you lost control. The advantage bar shows when the position shifted." },
              ].map(({ mistake, fix }) => (
                <div key={mistake} className="p-4 rounded-xl border border-red-500/10 bg-background">
                  <div className="flex gap-2 mb-2">
                    <span className="text-red-400 text-xs font-bold shrink-0 mt-0.5">✗</span>
                    <p className="text-sm font-semibold">{mistake}</p>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-green-400 text-xs font-bold shrink-0 mt-0.5">✓</span>
                    <p className="text-sm text-muted-foreground leading-relaxed">{fix}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ── AI Opponents ── */}
          <section id="bots" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                <Cpu className="w-4 h-4 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">AI Opponents</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              There are four AI bots available, each with a different playstyle and difficulty. Start with Randy and work your way up.
            </p>
            <div className="space-y-3">
              {[
                { icon: "🎲", name: "Randy", diff: 1, desc: "Plays completely randomly. Good for learning the basic flow of the game without any pressure." },
                { icon: "🤑", name: "Greedy", diff: 2, desc: "Prioritizes winning mini-boards immediately whenever possible. Predictable but can catch beginners off guard." },
                { icon: "☘️", name: "Jardinerito", diff: 3, desc: "Uses a heuristic evaluation to make smarter decisions. Thinks about board control and forced moves." },
                { icon: "🍀", name: "Jardinero", diff: 4, desc: "The strongest bot. Uses deep search with pruning and positional evaluation. A genuine challenge even for experienced players." },
              ].map(({ icon, name, diff, desc }) => (
                <div key={name} className="flex gap-4 p-4 rounded-xl border border-border/50 bg-background">
                  <span className="text-2xl leading-none shrink-0 mt-0.5">{icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <p className="text-sm font-semibold">{name}</p>
                      <div className="flex gap-0.5">
                        {Array(5).fill(0).map((_, i) => (
                          <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < diff ? "bg-green-500" : "bg-border"}`} />
                        ))}
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ── FAQ ── */}
          <section id="faq" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center shrink-0">
                <HelpCircle className="w-4 h-4 text-indigo-400" />
              </div>
              <h2 className="text-2xl font-bold">FAQ</h2>
            </div>
            <div className="space-y-3">
              {[
                { q: "What happens if I'm sent to a board that's already won?", a: "You get a free choice — you can play in any open board on the big grid. This is why sending your opponent to a won board is usually bad for you." },
                { q: "Can a drawn mini-board be used to win the big board?", a: "No. A drawn mini-board is neutral — it doesn't count for either player. Only won boards count toward the big board." },
                { q: "What if all 9 boards are resolved but nobody won the big board?", a: "The game ends in a draw. This is rare but possible." },
                { q: "Can I play on any board at the start?", a: "Yes. The very first move of the game is a free choice — X can play in any cell of any board." },
                { q: "Does the game have a time limit?", a: "Only if you choose a time control when setting up the game. You can also play with no time limit." },
                { q: "Can I rejoin a game if I accidentally close the tab?", a: "Yes. As long as you reopen the game within 5 minutes, you'll be automatically reconnected to your active session." },
                { q: "Is there an undo button?", a: "No. Moves are final once submitted, just like in a real game." },
              ].map(({ q, a }) => (
                <div key={q} className="p-4 rounded-xl border border-border/50 bg-background">
                  <p className="text-sm font-semibold mb-1.5">{q}</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{a}</p>
                </div>
              ))}
            </div>
          </section>

          {/* ── Tips ── */}
          <section id="tips" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center shrink-0">
                <Zap className="w-4 h-4 text-orange-400" />
              </div>
              <h2 className="text-2xl font-bold">Tips for Beginners</h2>
            </div>
            <ul className="space-y-2">
              {[
                "Don't overthink your first few moves — focus on understanding the forced-move mechanic before worrying about strategy.",
                "Keep your eye on the whole board, not just the mini-board you're playing in. The big picture matters more.",
                "Play against Randy first to get comfortable with the flow, then step up to Greedy once you understand the rules.",
                "Use the move history panel after a loss to find the exact move where you lost control.",
                "Hover over won boards to reveal the cells inside — useful for reviewing the game state.",
                "The advantage bar in the side panel updates after every move. Watch it to understand when the position shifts.",
                "In online games, if your opponent disconnects, wait — they have 5 minutes to rejoin before the game is abandoned.",
              ].map((tip) => (
                <li key={tip} className="flex gap-3 text-sm text-muted-foreground leading-relaxed">
                  <span className="text-orange-400 mt-0.5 shrink-0">→</span>
                  {tip}
                </li>
              ))}
            </ul>
          </section>

          <div className="pt-4 border-t border-border/50 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">Ready to put it into practice?</p>
            <Link href="/play" className="inline-flex items-center gap-2 px-6 py-2.5 bg-green-600 hover:bg-green-500 text-white text-sm font-semibold rounded-lg transition-colors">
              Play Now <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
