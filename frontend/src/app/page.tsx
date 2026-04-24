"use client";
import React, { useEffect, useRef, useMemo } from "react";
import Link from "next/link";

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
    () => shuffleArray([
      "strategy", "skill", "luck", "tactics", "planning", "execution",
      "decision-making", "expertise", "wit", "probability", "preparation",
      "risk", "adaptability",
    ]),
    []
  );

  const shuffledColors = useMemo(
    () => shuffleArray([
      "#FFD700", "#FF4500", "#00FF00", "#1E90FF", "#FF69B4", "#8A2BE2",
      "#00CED1", "#FFA500", "#7FFF00", "#DC143C", "#4682B4", "#D2691E", "#808080",
    ]),
    []
  );

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
    <div className="flex flex-col items-center justify-center min-h-svh p-6">
      <h1 className="mb-10 text-3xl font-bold sm:text-4xl text-center">
        <small>Welcome to the</small>
        <br />
        <span>Ultimate Tic-Tac-Toe,</span>
        <br />
        <small>a game of <span ref={typeRef}></span>.</small>
      </h1>

      <Link
        href="/play"
        className="px-10 py-3.5 bg-green-600 hover:bg-green-500 text-white text-lg font-semibold rounded-lg transition-colors"
      >
        Play
      </Link>
    </div>
  );
}
