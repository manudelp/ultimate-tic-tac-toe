"use client";
import React, { useEffect, useRef, useMemo } from "react";
import Button from "@/components/ui/button";
import Share from "@/components/ui/share";
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
  // Ref for the typing effect
  const typeRef = useRef<HTMLSpanElement>(null);

  // Typing Words and Colors
  const shuffledWords = useMemo(
    () =>
      shuffleArray([
        "strategy",
        "skill",
        "luck",
        "tactics",
        "planning",
        "execution",
        "decision-making",
        "expertise",
        "wit",
        "probability",
        "preparation",
        "risk",
        "adaptability",
      ]),
    []
  );

  const shuffledColors = useMemo(
    () =>
      shuffleArray([
        "#FFD700",
        "#FF4500",
        "#00FF00",
        "#1E90FF",
        "#FF69B4",
        "#8A2BE2",
        "#00CED1",
        "#FFA500",
        "#7FFF00",
        "#DC143C",
        "#4682B4",
        "#D2691E",
        "#808080",
      ]),
    []
  );

  // Words effect
  useEffect(() => {
    if (!typeRef.current) return;

    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let animationFrame: number;

    const type = () => {
      const currentWord = shuffledWords[wordIndex];

      // Update text content
      if (typeRef.current) {
        typeRef.current.textContent = isDeleting
          ? currentWord.substring(0, charIndex--)
          : currentWord.substring(0, charIndex++);
        typeRef.current.style.color = shuffledColors[wordIndex];
      }

      // Handle typing/deleting transitions
      if (!isDeleting && charIndex === currentWord.length + 1) {
        // Pause when the full word is typed
        setTimeout(() => {
          isDeleting = true;
          animationFrame = requestAnimationFrame(type);
        }, 1000); // Pause before starting deletion
      } else if (isDeleting && charIndex === 0) {
        // Switch to the next word when deletion is complete
        isDeleting = false;
        wordIndex = (wordIndex + 1) % shuffledWords.length;
        animationFrame = requestAnimationFrame(type);
      } else {
        // Adjust typing speed based on state
        const speed = isDeleting ? 50 : 100;
        setTimeout(() => {
          animationFrame = requestAnimationFrame(type);
        }, speed);
      }
    };

    // Start typing
    animationFrame = requestAnimationFrame(type);

    // Cleanup
    return () => cancelAnimationFrame(animationFrame);
  }, [shuffledWords, shuffledColors]);

  return (
    <div className=" min-h-svh">
      <div className="flex flex-col items-center justify-center p-4 text-white min-h-svh sm:p-8">
        <div className="text-center">
          {/* Title */}
          <h1 className="mb-8 text-3xl font-bold sm:text-4xl">
            <small>Welcome to the</small>
            <br />
            <span className="relative">Ultimate Tic-Tac-Toe,</span>
            <br />
            <small>
              a game of <span id="type" ref={typeRef}></span>.
            </small>
          </h1>

          {/* Choose Game Mode */}
          <div className="flex flex-col flex-wrap justify-center gap-6 sm:flex-row">
            <Link href="pvp">
              <Button
                text="Fight someone"
                className="text-lg font-medium hover:bg-green-700 hover:animate-pulse"
              />
            </Link>
            <Link href="bot">
              <Button
                text="Fight us"
                className="text-lg font-medium bg-gray-800 hover:bg-red-700"
              />
            </Link>
          </div>
          <Share />
        </div>
      </div>
    </div>
  );
}
