import Link from "next/link";
import { Target, BookOpen, Trophy, Lightbulb, Zap, ArrowRight, Info } from "lucide-react";

const SECTIONS = [
  { id: "objective", title: "Objective", icon: Target },
  { id: "rules", title: "Rules", icon: BookOpen },
  { id: "winning", title: "Winning", icon: Trophy },
  { id: "strategies", title: "Strategies", icon: Lightbulb },
  { id: "tips", title: "Tips", icon: Zap },
];

export default function Learn() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-8 py-12">

      {/* Header */}
      <div className="mb-12">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Guide</p>
        <h1 className="text-4xl font-bold mb-3">How to Play</h1>
        <p className="text-muted-foreground text-base leading-relaxed max-w-xl">
          Ultimate Tic-Tac-Toe looks simple but rewards deep thinking. Learn the rules, then master the strategy.
        </p>
      </div>

      <div className="flex gap-12">

        {/* Sticky sidebar */}
        <aside className="hidden md:flex flex-col gap-1 w-44 shrink-0">
          <div className="sticky top-20">
            <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground mb-3 px-2">On this page</p>
            {SECTIONS.map(({ id, title, icon: Icon }) => (
              <a
                key={id}
                href={`#${id}`}
                className="flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-surface transition-colors"
              >
                <Icon className="w-3.5 h-3.5 shrink-0" />
                {title}
              </a>
            ))}
          </div>
        </aside>

        {/* Mobile nav */}
        <div className="md:hidden flex flex-wrap gap-2 mb-8 w-full">
          {SECTIONS.map(({ id, title }) => (
            <a key={id} href={`#${id}`} className="text-xs px-3 py-1.5 bg-surface rounded-full text-muted-foreground hover:text-foreground transition-colors">
              {title}
            </a>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-16">

          <section id="objective" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                <Target className="w-4 h-4 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">Objective</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Ultimate Tic-Tac-Toe is played on a 3×3 grid of smaller Tic-Tac-Toe boards.
              Win three small boards in a row — horizontally, vertically, or diagonally — to win the game.
            </p>
            <div className="flex gap-3 p-4 rounded-xl border border-blue-500/20 bg-blue-500/5">
              <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground leading-relaxed">
                Think of it as regular Tic-Tac-Toe, but each cell <em>is</em> its own Tic-Tac-Toe game.
                Win the small game to claim that cell on the big board.
              </p>
            </div>
          </section>

          <section id="rules" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center shrink-0">
                <BookOpen className="w-4 h-4 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold">Rules</h2>
            </div>
            <div className="space-y-3">
              {[
                { n: "1", text: "Play your mark in any empty cell of an available mini-board." },
                { n: "2", text: "The cell you pick determines which mini-board your opponent must play in next. Play in the top-left cell → opponent plays in the top-left mini-board.", highlight: true },
                { n: "3", text: "If sent to a board that is already won or completely full, your opponent may play in any open board." },
                { n: "4", text: "Win a mini-board by getting three of your marks in a row within it." },
              ].map(({ n, text, highlight }) => (
                <div key={n} className={`flex gap-4 p-4 rounded-xl border ${highlight ? "border-purple-500/20 bg-purple-500/5" : "border-border/50 bg-background"}`}>
                  <span className={`text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${highlight ? "bg-purple-500/20 text-purple-400" : "bg-surface text-muted-foreground"}`}>{n}</span>
                  <p className="text-sm text-muted-foreground leading-relaxed">{text}</p>
                </div>
              ))}
            </div>
          </section>

          <section id="winning" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center shrink-0">
                <Trophy className="w-4 h-4 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold">Winning</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Win three mini-boards in a row on the larger grid — just like regular Tic-Tac-Toe.
              If all boards are filled with no winner, the game ends in a draw.
            </p>
            <div className="flex gap-3 p-4 rounded-xl border border-green-500/20 bg-green-500/5">
              <Info className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground leading-relaxed">
                A mini-board that ends in a draw is considered neutral — it doesn&apos;t count for either player on the big board.
              </p>
            </div>
          </section>

          <section id="strategies" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center shrink-0">
                <Lightbulb className="w-4 h-4 text-yellow-400" />
              </div>
              <h2 className="text-2xl font-bold">Strategies</h2>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {[
                { title: "Plan ahead", desc: "Always think about where your move sends your opponent, not just whether it wins the current mini-board." },
                { title: "Control the center", desc: "The center mini-board connects to the most winning lines. Winning it early gives you a structural advantage." },
                { title: "Send them to bad boards", desc: "Force your opponent into boards where they have no good moves — won boards, full boards, or boards where you're already winning." },
                { title: "Balance offense and defense", desc: "Sometimes blocking your opponent from winning a mini-board is more valuable than advancing your own position." },
              ].map(({ title, desc }) => (
                <div key={title} className="p-4 rounded-xl border border-border/50 bg-background">
                  <h3 className="text-sm font-semibold mb-1.5">{title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </section>

          <section id="tips" className="scroll-mt-20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center shrink-0">
                <Zap className="w-4 h-4 text-orange-400" />
              </div>
              <h2 className="text-2xl font-bold">Tips for Beginners</h2>
            </div>
            <ul className="space-y-2">
              {[
                "Don't overthink your first few moves — focus on understanding the flow of the game.",
                "Keep your eye on the whole board, not just the mini-board you're playing in.",
                "Play against Randy (the random bot) first to get comfortable before facing harder opponents.",
                "Use the move history panel to review your games and spot where you lost control.",
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
            <Link
              href="/play"
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-green-600 hover:bg-green-500 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              Play Now <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
