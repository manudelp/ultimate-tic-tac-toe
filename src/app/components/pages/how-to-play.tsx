import React from "react";
import { Link } from "react-router-dom";

const HowToPlay: React.FC = () => {
  return (
    <div className="container m-auto max-w-3xl py-8 px-4 text-white">
      <h1 className="mt-16 text-3xl font-bold mb-6 text-center">
        How to Play Ultimate Tic-Tac-Toe
      </h1>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Objective of the Game</h2>
        <p className="text-base leading-relaxed">
          Ultimate Tic-Tac-Toe is a strategic twist on the classic Tic-Tac-Toe.
          Instead of one small 3x3 grid, you play on a larger 3x3 grid of
          smaller Tic-Tac-Toe boards. The objective is to win three small boards
          in a row, either horizontally, vertically, or diagonally, to win the
          overall game.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Game Setup</h2>
        <ul className="list-disc pl-6 text-base leading-relaxed">
          <li>
            The game consists of nine mini Tic-Tac-Toe boards arranged in a 3x3
            grid.
          </li>
          <li>
            Each player takes turns playing either &apos;X&apos; or
            &apos;O&apos;.
          </li>
          <li>
            The players alternate turns, just like in regular Tic-Tac-Toe.
          </li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Gameplay Rules</h2>
        <ol className="list-decimal pl-6 text-base leading-relaxed">
          <li>
            On your turn, you must play your mark (&apos;X&apos; or
            &apos;O&apos;) in one of the empty cells in any of the mini boards.
          </li>
          <li>
            The board you choose must follow this rule:
            <strong>
              {" "}
              Your move determines the next board for your opponent.
            </strong>
            <p className="ml-6">
              For example, if you play in the top-left corner of any mini-board,
              your opponent must play in the top-left mini-board on their next
              turn.
            </p>
          </li>
          <li>
            If your move sends your opponent to a mini-board that is already won
            or full, they can play anywhere on the larger grid.
          </li>
          <li>
            To win a mini-board, you must achieve a regular Tic-Tac-Toe win
            within that mini-board (three in a row, either horizontally,
            vertically, or diagonally).
          </li>
        </ol>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Winning the Game</h2>
        <p className="text-base leading-relaxed">
          The goal of Ultimate Tic-Tac-Toe is to win three mini-boards in a row
          on the larger board. You can win the game by achieving three wins in a
          row either:
        </p>
        <ul className="list-disc pl-6 text-base leading-relaxed">
          <li>Horizontally</li>
          <li>Vertically</li>
          <li>Diagonally</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Advanced Strategies</h2>
        <ul className="list-disc pl-6 text-base leading-relaxed">
          <li>
            <strong>Plan Ahead:</strong> Since your move determines where your
            opponent plays, think ahead about where you&apos;re sending them.
            Try to send them to boards where they don&apos;t have a strong
            position or are forced to block your move.
          </li>
          <li>
            <strong>Force a Win:</strong> If your opponent sends you to a board
            where you can win, you must seize the opportunity, but also be
            careful to avoid setting them up for wins as well...
          </li>
          <li>
            <strong>Play Defensively:</strong> Sometimes it&apos;s better to
            block your opponent’s potential win rather than focusing solely on
            your own. Balancing between offense and defense is key to Ultimate
            Tic-Tac-Toe.
          </li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Special Situations</h2>
        <ul className="list-disc pl-6 text-base leading-relaxed">
          <li>
            <strong>Full Boards:</strong> If a mini-board is completely filled
            with no winner, it is considered a draw and that board is no longer
            available for play. However, it still counts as part of the larger
            grid, meaning your move may direct your opponent to a full or drawn
            board.
          </li>
          <li>
            <strong>Locked Boards:</strong> Once a player wins a mini-board, no
            further moves can be made on that board, and it remains locked with
            the winner&apos;s mark for the rest of the game. This is also true
            when a board is full (drawn)
          </li>
          <li>
            <strong>Ties:</strong> If the larger grid is filled with no overall
            winner (no player has three mini-board wins in a row and all boards
            are locked), the game ends in a draw.
          </li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Tips for Beginners</h2>
        <ul className="list-disc pl-6 text-base leading-relaxed">
          <li>
            <strong>Start Simple:</strong> Don’t overthink your first few moves.
            Just focus on learning how the board works.
          </li>
          <li>
            <strong>Focus on Control:</strong> Pay attention to where your move
            sends your opponent. Maintaining control of where they play can give
            you a huge advantage.
          </li>
          <li>
            <strong>Watch the Whole Board:</strong> Don’t just focus on one
            mini-board. Pay attention to the overall game to avoid getting
            surprised by your opponent’s strategy.
          </li>
        </ul>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4">Game Modes</h2>
        <ul className="list-disc pl-6 text-base leading-relaxed">
          <li>
            <strong>Player vs. Player:</strong> Play against another human
            player.
          </li>
          <li>
            <strong>Player vs. Bot:</strong> Challenge an AI opponent with
            varying difficulty levels.
          </li>
          <li>
            <strong>Bot vs. Bot:</strong> Watch AI players compete against each
            other for fun or for analysis.
          </li>
        </ul>
      </section>

      <Link to="/">
        <button className="mt-8 transition bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Play Now
        </button>
      </Link>
    </div>
  );
};

export default HowToPlay;
