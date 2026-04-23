"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const HIDDEN_ROUTES = ["/pvp/lobby", "/pvp/matchmaking"];

export default function Header() {
  const pathname = usePathname();

  if (HIDDEN_ROUTES.some((r) => pathname.startsWith(r))) return null;

  return (
    <header className="w-full bg-gray-900/80 backdrop-blur-sm border-b border-gray-800/50">
      <div className="container mx-auto px-4 py-2 flex items-center justify-between">
        <Link href="/" className="text-lg font-bold hover:text-gray-300 transition-colors">
          Ultimate Tic-Tac-Toe
        </Link>
        <div className="flex gap-2">
          <Link
            href="/pvp"
            className="px-3 py-1.5 text-sm rounded bg-gray-800 hover:bg-gray-700 transition-colors"
          >
            vs Player
          </Link>
          <Link
            href="/bot"
            className="px-3 py-1.5 text-sm rounded bg-gray-800 hover:bg-gray-700 transition-colors"
          >
            vs Bot
          </Link>
        </div>
      </div>
    </header>
  );
}
