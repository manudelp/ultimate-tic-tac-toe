"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Gamepad2, BookOpen } from "lucide-react";

const NAV = [
  { href: "/play", icon: Gamepad2, label: "Play" },
  { href: "/learn", icon: BookOpen, label: "Learn" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const inGame = pathname.startsWith("/game");

  if (inGame) return null;

  const active = (href: string) => pathname.startsWith(href);

  return (
    <>
      {/* Desktop */}
      <aside className="hidden md:flex fixed left-0 top-0 bottom-0 z-30 w-48 flex-col bg-gray-900 border-r border-gray-800">
        <Link href="/" className="flex items-center px-5 h-14 border-b border-gray-800 shrink-0">
          <span className="text-base font-bold">Ultimate Tic-Tac-Toe</span>
        </Link>

        <nav className="flex flex-col gap-1 py-3 px-3 flex-1">
          {NAV.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                active(href)
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800/50"
              }`}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {label}
            </Link>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-gray-800 text-[11px] text-gray-600 space-y-1">
          <div className="flex gap-2">
            <Link href="/privacy-policy" className="hover:text-gray-400 transition-colors">Privacy</Link>
            <span>&middot;</span>
            <Link href="/terms-of-service" className="hover:text-gray-400 transition-colors">Terms</Link>
          </div>
          <p>&copy; {new Date().getFullYear()} Ultimate Tic-Tac-Toe</p>
        </div>
      </aside>

      {/* Mobile bottom bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-gray-900 border-t border-gray-800 safe-bottom">
        <div className="flex justify-around py-2">
          {NAV.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-0.5 px-4 py-1 transition-colors ${
                active(href) ? "text-white" : "text-gray-500"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px]">{label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </>
  );
}
