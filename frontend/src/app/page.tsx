"use client";
import { useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import { Bot, Globe, Users } from "lucide-react";
import HeroBoard from "@/components/core/hero-board";

const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

const WORDS = [
  "strategy", "skill", "luck", "tactics", "planning", "execution",
  "decision-making", "expertise", "wit", "probability", "preparation",
  "risk", "adaptability",
];

const COLORS = [
  "#FFD700", "#FF4500", "#00FF00", "#1E90FF", "#FF69B4", "#8A2BE2",
  "#00CED1", "#FFA500", "#7FFF00", "#DC143C", "#4682B4", "#D2691E", "#808080",
];

const STEPS = [
  { num: "1", title: "Pick a cell", desc: "Play your mark in any available mini-board." },
  { num: "2", title: "Direct your opponent", desc: "Your cell choice decides which board they play next." },
  { num: "3", title: "Win the big board", desc: "Claim three mini-boards in a row to win the game." },
];

const MODES = [
  { icon: Bot, title: "vs AI", desc: "Challenge bots from beginner to expert difficulty." },
  { icon: Globe, title: "Online", desc: "Play friends in private lobbies or find a random opponent." },
  { icon: Users, title: "Local", desc: "Pass and play on the same device." },
];

export default function Home() {
  const typeRef = useRef<HTMLSpanElement>(null);

  const shuffledWords = useMemo(() => shuffleArray(WORDS), []);
  const shuffledColors = useMemo(() => shuffleArray(COLORS), []);

  useEffect(() => {
    if (!typeRef.current) return;
    let wordIndex = 0, charIndex = 0, isDeleting = false, frame: number;

    const tick = () => {
      const word = shuffledWords[wordIndex];
      if (typeRef.current) {
        typeRef.current.textContent = isDeleting
          ? word.substring(0, charIndex--)
          : word.substring(0, charIndex++);
        typeRef.current.style.color = shuffledColors[wordIndex];
      }
      if (!isDeleting && charIndex === word.length + 1) {
        setTimeout(() => { isDeleting = true; frame = requestAnimationFrame(tick); }, 1000);
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        wordIndex = (wordIndex + 1) % shuffledWords.length;
        frame = requestAnimationFrame(tick);
      } else {
        setTimeout(() => { frame = requestAnimationFrame(tick); }, isDeleting ? 50 : 100);
      }
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [shuffledWords, shuffledColors]);

  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="relative min-h-[75vh] flex flex-col">
        <nav className="flex items-center justify-between px-4 sm:px-6 h-14 shrink-0">
          <span className="text-base font-bold">Ultimate Tic-Tac-Toe</span>
          <Link href="/learn" className="text-sm text-gray-400 hover:text-white transition-colors">
            How to Play
          </Link>
        </nav>

        <div className="flex-1 flex flex-col md:flex-row items-center justify-center gap-10 md:gap-16 px-6 pb-12">
          <div className="flex flex-col items-center md:items-start text-center md:text-left">
            <h1 className="mb-8 flex flex-col gap-2">
              <span className="text-gray-400 text-xl sm:text-2xl font-medium">Welcome to the</span>
              <span className="text-3xl sm:text-5xl font-bold">Ultimate Tic-Tac-Toe,</span>
              <span className="text-xl sm:text-2xl font-medium text-gray-400">
                a game of <span ref={typeRef} className="font-bold" />.
              </span>
            </h1>

            <Link
              href="/play"
              className="px-10 py-3.5 bg-green-600 hover:bg-green-500 text-white text-lg font-semibold rounded-lg transition-colors"
            >
              Play Now
            </Link>
          </div>

          <div className="opacity-60 pointer-events-none">
            <HeroBoard />
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 py-20 bg-gray-800/40">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.num} className="flex flex-col items-center text-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 text-blue-400 font-bold text-lg flex items-center justify-center">
                  {s.num}
                </div>
                <h3 className="font-semibold">{s.title}</h3>
                <p className="text-sm text-gray-400">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Game modes */}
      <section className="px-6 py-20">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-12">Game Modes</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {MODES.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="p-5 bg-gray-800 rounded-lg border border-gray-700 flex flex-col items-center text-center gap-3">
                <Icon className="w-8 h-8 text-gray-300" />
                <h3 className="font-semibold">{title}</h3>
                <p className="text-sm text-gray-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-6 py-20 bg-gray-800/40 text-center">
        <h2 className="text-2xl font-bold mb-4">Ready to play?</h2>
        <p className="text-gray-400 mb-8">No account needed. Jump straight in.</p>
        <Link
          href="/play"
          className="px-10 py-3.5 bg-green-600 hover:bg-green-500 text-white text-lg font-semibold rounded-lg transition-colors"
        >
          Start Playing
        </Link>
      </section>

      {/* Footer */}
      <footer className="flex items-center justify-center gap-3 py-4 text-[11px] text-gray-600">
        <span>&copy; {new Date().getFullYear()} Ultimate Tic-Tac-Toe</span>
        <span>&middot;</span>
        <span>Built by{" "}
          <a href="https://www.linkedin.com/in/manuel-delpino/" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">Manuel Delpino</a>
          {" & "}
          <a href="https://www.linkedin.com/in/manuel-meiri%C3%B1o-7b9214331/" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">Manuel Meiriño</a>
        </span>
        <span>&middot;</span>
        <Link href="/privacy-policy" className="hover:text-gray-400 transition-colors">Privacy</Link>
        <span>&middot;</span>
        <Link href="/terms-of-service" className="hover:text-gray-400 transition-colors">Terms</Link>
      </footer>
    </div>
  );
}
