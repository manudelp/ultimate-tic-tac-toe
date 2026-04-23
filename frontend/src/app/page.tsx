"use client";
import React, { useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import { Bot, Globe, Users } from "lucide-react";

const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

export default function Home() {
  const typeRef = useRef<HTMLSpanElement>(null);

  const shuffledWords = useMemo(
    () =>
      shuffleArray([
        "strategy", "skill", "luck", "tactics", "planning", "execution",
        "decision-making", "expertise", "wit", "probability", "preparation",
        "risk", "adaptability",
      ]),
    []
  );

  const shuffledColors = useMemo(
    () =>
      shuffleArray([
        "#FFD700", "#FF4500", "#00FF00", "#1E90FF", "#FF69B4", "#8A2BE2",
        "#00CED1", "#FFA500", "#7FFF00", "#DC143C", "#4682B4", "#D2691E",
        "#808080",
      ]),
    []
  );

  useEffect(() => {
    if (!typeRef.current) return;

    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let animationFrame: number;

    const type = () => {
      const currentWord = shuffledWords[wordIndex];

      if (typeRef.current) {
        typeRef.current.textContent = isDeleting
          ? currentWord.substring(0, charIndex--)
          : currentWord.substring(0, charIndex++);
        typeRef.current.style.color = shuffledColors[wordIndex];
      }

      if (!isDeleting && charIndex === currentWord.length + 1) {
        setTimeout(() => {
          isDeleting = true;
          animationFrame = requestAnimationFrame(type);
        }, 1000);
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        wordIndex = (wordIndex + 1) % shuffledWords.length;
        animationFrame = requestAnimationFrame(type);
      } else {
        const speed = isDeleting ? 50 : 100;
        setTimeout(() => {
          animationFrame = requestAnimationFrame(type);
        }, speed);
      }
    };

    animationFrame = requestAnimationFrame(type);
    return () => cancelAnimationFrame(animationFrame);
  }, [shuffledWords, shuffledColors]);

  return (
    <div className="min-h-svh flex flex-col">
      {/* Hero — the sacred brand */}
      <div className="flex flex-col items-center justify-center p-4 sm:p-8 flex-1">
        <h1 className="mb-12 text-3xl font-bold sm:text-4xl text-center">
          <small>Welcome to the</small>
          <br />
          <span>Ultimate Tic-Tac-Toe,</span>
          <br />
          <small>
            a game of <span ref={typeRef}></span>.
          </small>
        </h1>

        {/* Play Hub */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl">
          <Link href="/bot" className="group">
            <div className="flex flex-col items-center gap-3 p-6 bg-gray-800 border border-gray-700 rounded-lg transition-all hover:border-red-500/50 hover:bg-gray-800/80 group-hover:scale-[1.02]">
              <Bot className="w-8 h-8 text-red-400" />
              <h2 className="text-lg font-semibold">vs AI</h2>
              <p className="text-sm text-gray-400 text-center">
                Challenge AI opponents
              </p>
            </div>
          </Link>

          <Link href="/pvp?mode=online" className="group">
            <div className="flex flex-col items-center gap-3 p-6 bg-gray-800 border border-gray-700 rounded-lg transition-all hover:border-green-500/50 hover:bg-gray-800/80 group-hover:scale-[1.02]">
              <Globe className="w-8 h-8 text-green-400" />
              <h2 className="text-lg font-semibold">Online</h2>
              <p className="text-sm text-gray-400 text-center">
                Play against anyone
              </p>
            </div>
          </Link>

          <Link href="/pvp?mode=local" className="group">
            <div className="flex flex-col items-center gap-3 p-6 bg-gray-800 border border-gray-700 rounded-lg transition-all hover:border-blue-500/50 hover:bg-gray-800/80 group-hover:scale-[1.02]">
              <Users className="w-8 h-8 text-blue-400" />
              <h2 className="text-lg font-semibold">Local</h2>
              <p className="text-sm text-gray-400 text-center">
                Same device, two players
              </p>
            </div>
          </Link>
        </div>

        <Link
          href="/how-to-play"
          className="mt-8 text-sm text-gray-500 hover:text-gray-300 transition-colors"
        >
          New here? Learn how to play →
        </Link>
      </div>
    </div>
  );
}
