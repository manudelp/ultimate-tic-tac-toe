import React from "react";
import Link from "next/link";

const HowToPlay: React.FC = () => {
  const sections = [
    { id: "objective", title: "Objective" },
    { id: "setup", title: "Setup" },
    { id: "rules", title: "Rules" },
    { id: "winning", title: "Winning" },
    { id: "strategies", title: "Strategies" },
    { id: "special", title: "Special Cases" },
    { id: "tips", title: "Tips" },
    { id: "modes", title: "Game Modes" },
  ];

  return (
    <div className="pt-20 pb-12">
      {/* Mobile: horizontal scrolling nav */}
      <div className="md:hidden sticky top-14 z-10 bg-gray-900/90 backdrop-blur-sm border-b border-gray-800 px-4 py-3 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-700">
        <div className="flex gap-3 min-w-max">
          {sections.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              className="text-sm text-gray-400 hover:text-white transition-colors whitespace-nowrap px-2 py-1 rounded bg-gray-800"
            >
              {s.title}
            </a>
          ))}
        </div>
      </div>

      <div className="flex justify-center max-w-5xl mx-auto px-4">
        {/* Desktop: sidebar */}
        <aside className="hidden md:block sticky top-20 h-fit w-56 shrink-0 pr-8 border-r border-gray-800">
          <h3 className="text-lg font-bold mb-4">Contents</h3>
          <nav>
            <ul className="space-y-2 text-sm">
              {sections.map((s) => (
                <li key={s.id}>
                  <a
                    href={`#${s.id}`}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    {s.title}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
          <Link href="/">
            <button className="mt-8 w-full transition bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded text-sm">
              Play Now
            </button>
          </Link>
        </aside>

        {/* Main content */}
        <div className="max-w-3xl md:pl-8">
          <h1 className="text-3xl font-bold mb-6">
            How to Play Ultimate Tic-Tac-Toe
          </h1>

          <section id="objective" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Objective of the Game</h2>
            <p className="text-gray-300 leading-relaxed">
              Ultimate Tic-Tac-Toe is a strategic twist on the classic
              Tic-Tac-Toe. Instead of one small 3x3 grid, you play on a larger
              3x3 grid of smaller Tic-Tac-Toe boards. The objective is to win
              three small boards in a row, either horizontally, vertically, or
              diagonally, to win the overall game.
            </p>
          </section>

          <section id="setup" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Game Setup</h2>
            <ul className="list-disc pl-6 text-gray-300 leading-relaxed space-y-1">
              <li>The game consists of nine mini Tic-Tac-Toe boards arranged in a 3x3 grid.</li>
              <li>Each player takes turns playing either &apos;X&apos; or &apos;O&apos;.</li>
              <li>The players alternate turns, just like in regular Tic-Tac-Toe.</li>
            </ul>
          </section>

          <section id="rules" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Gameplay Rules</h2>
            <ol className="list-decimal pl-6 text-gray-300 leading-relaxed space-y-2">
              <li>On your turn, play your mark in one of the empty cells in any available mini board.</li>
              <li>
                <strong>Your move determines the next board for your opponent.</strong>
                <p className="ml-4 mt-1 text-gray-400">
                  For example, if you play in the top-left cell of any mini-board,
                  your opponent must play in the top-left mini-board next.
                </p>
              </li>
              <li>If your move sends your opponent to a board that is already won or full, they can play anywhere.</li>
              <li>Win a mini-board by getting three in a row within it (horizontally, vertically, or diagonally).</li>
            </ol>
          </section>

          <section id="winning" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Winning the Game</h2>
            <p className="text-gray-300 leading-relaxed">
              Win three mini-boards in a row on the larger board — horizontally,
              vertically, or diagonally.
            </p>
          </section>

          <section id="strategies" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Advanced Strategies</h2>
            <ul className="list-disc pl-6 text-gray-300 leading-relaxed space-y-2">
              <li>
                <strong>Plan Ahead:</strong> Your move determines where your opponent plays.
                Send them to boards where they&apos;re weak.
              </li>
              <li>
                <strong>Force a Win:</strong> Seize opportunities when sent to a winnable board,
                but avoid setting up your opponent.
              </li>
              <li>
                <strong>Play Defensively:</strong> Sometimes blocking your opponent&apos;s win
                is more valuable than pursuing your own.
              </li>
            </ul>
          </section>

          <section id="special" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Special Situations</h2>
            <ul className="list-disc pl-6 text-gray-300 leading-relaxed space-y-2">
              <li>
                <strong>Full Boards:</strong> A filled mini-board with no winner is a draw.
                Your move may still direct your opponent there.
              </li>
              <li>
                <strong>Locked Boards:</strong> Won or drawn boards are locked — no further moves allowed.
              </li>
              <li>
                <strong>Ties:</strong> If all boards are locked with no overall winner, the game is a draw.
              </li>
            </ul>
          </section>

          <section id="tips" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Tips for Beginners</h2>
            <ul className="list-disc pl-6 text-gray-300 leading-relaxed space-y-2">
              <li><strong>Start Simple:</strong> Focus on learning how the board works before overthinking.</li>
              <li><strong>Focus on Control:</strong> Where you send your opponent matters as much as where you play.</li>
              <li><strong>Watch the Whole Board:</strong> Don&apos;t tunnel-vision on one mini-board.</li>
            </ul>
          </section>

          <section id="modes" className="mb-8 scroll-mt-28 md:scroll-mt-8">
            <h2 className="text-2xl font-semibold mb-4">Game Modes</h2>
            <ul className="list-disc pl-6 text-gray-300 leading-relaxed space-y-1">
              <li>
                <Link href="/pvp" className="font-medium hover:text-blue-400 transition-colors">
                  Fight someone
                </Link>{" "}
                — Play against another human player locally or online.
              </li>
              <li>
                <Link href="/bot" className="font-medium hover:text-blue-400 transition-colors">
                  Fight us
                </Link>{" "}
                — Challenge an AI opponent with varying difficulty levels.
              </li>
            </ul>
          </section>

          {/* Mobile play button */}
          <div className="md:hidden flex justify-center">
            <Link href="/">
              <button className="transition bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded">
                Play Now
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowToPlay;
