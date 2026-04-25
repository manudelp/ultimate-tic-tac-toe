"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Gamepad2, BookOpen } from "lucide-react";

const NAV = [
  { href: "/play", icon: Gamepad2, label: "Play" },
  { href: "/learn", icon: BookOpen, label: "Learn" },
];

export default function Header() {
  const pathname = usePathname();
  if (pathname === "/" || pathname.startsWith("/game")) return null;

  const active = (href: string) => pathname.startsWith(href);

  return (
    <>
    <header className="sticky top-0 z-30 flex items-center justify-between h-14 px-4 sm:px-6 bg-gray-900 border-b border-gray-800">
      <Link href="/" className="text-base font-bold whitespace-nowrap">
        Ultimate Tic-Tac-Toe
      </Link>

      <nav className="flex items-center gap-1">
        {NAV.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors ${
              active(href)
                ? "bg-gray-800 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-800/50"
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}
      </nav>
    </header>

    <footer className="fixed bottom-0 left-0 right-0 z-20 flex items-center justify-center gap-3 py-2 text-[11px] text-gray-600 bg-gray-900/80 backdrop-blur-sm border-t border-gray-800/50">
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
    </>
  );
}
