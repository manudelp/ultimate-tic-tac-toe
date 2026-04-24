import Link from "next/link";

const sections = [
  { id: "objective", title: "Objective" },
  { id: "rules", title: "Rules" },
  { id: "winning", title: "Winning" },
  { id: "strategies", title: "Strategies" },
  { id: "tips", title: "Tips" },
];

export default function Learn() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">How to Play</h1>

      <nav className="mb-8 flex flex-wrap gap-2">
        {sections.map((s) => (
          <a key={s.id} href={`#${s.id}`} className="text-sm px-3 py-1 bg-gray-800 rounded hover:bg-gray-700 transition-colors">
            {s.title}
          </a>
        ))}
      </nav>

      <div className="space-y-10 text-gray-300 leading-relaxed">
        <section id="objective" className="scroll-mt-8">
          <h2 className="text-2xl font-semibold text-white mb-3">Objective</h2>
          <p>
            Ultimate Tic-Tac-Toe is played on a 3x3 grid of smaller Tic-Tac-Toe boards.
            Win three small boards in a row (horizontally, vertically, or diagonally) to win the game.
          </p>
        </section>

        <section id="rules" className="scroll-mt-8">
          <h2 className="text-2xl font-semibold text-white mb-3">Rules</h2>
          <ol className="list-decimal pl-6 space-y-2">
            <li>Play your mark in any empty cell of an available mini-board.</li>
            <li>
              <strong className="text-white">Your move determines where your opponent plays next.</strong>{" "}
              If you play in the top-left cell, your opponent must play in the top-left mini-board.
            </li>
            <li>If sent to a won or full board, your opponent can play anywhere.</li>
            <li>Win a mini-board by getting three in a row within it.</li>
          </ol>
        </section>

        <section id="winning" className="scroll-mt-8">
          <h2 className="text-2xl font-semibold text-white mb-3">Winning</h2>
          <p>
            Win three mini-boards in a row on the larger grid. If all boards are filled
            with no winner, the game is a draw.
          </p>
        </section>

        <section id="strategies" className="scroll-mt-8">
          <h2 className="text-2xl font-semibold text-white mb-3">Strategies</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong className="text-white">Plan ahead:</strong> Think about where you&apos;re sending your opponent.</li>
            <li><strong className="text-white">Control the board:</strong> Send opponents to boards where they&apos;re weak.</li>
            <li><strong className="text-white">Balance offense and defense:</strong> Sometimes blocking is more valuable than attacking.</li>
          </ul>
        </section>

        <section id="tips" className="scroll-mt-8">
          <h2 className="text-2xl font-semibold text-white mb-3">Tips</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>Don&apos;t overthink your first moves — focus on learning the flow.</li>
            <li>Pay attention to the whole board, not just one mini-board.</li>
            <li>The center mini-board is strategically valuable.</li>
          </ul>
        </section>
      </div>

      <div className="mt-10 text-center">
        <Link
          href="/play"
          className="inline-block px-8 py-3 bg-green-600 hover:bg-green-500 text-white font-semibold rounded-lg transition-colors"
        >
          Play Now
        </Link>
      </div>
    </div>
  );
}
