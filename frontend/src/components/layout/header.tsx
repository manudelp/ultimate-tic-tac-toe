"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Gamepad2, BookOpen } from "lucide-react";
import ThemeToggle from "@/components/ui/theme-toggle";

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
    <header className="sticky top-0 z-30 flex items-center justify-between h-14 px-4 sm:px-6 bg-background border-b border-border">
      <Link href="/" className="text-base font-bold whitespace-nowrap">
        utictactoe
      </Link>

      <nav className="flex items-center gap-1">
        {NAV.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors ${
              active(href)
                ? "bg-accent text-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}
        <ThemeToggle />
      </nav>
    </header>

    {/* Spacer for fixed footer */}
    <div className="h-12" />

    <footer className="fixed bottom-0 left-0 right-0 z-20 flex items-center justify-center flex-wrap gap-x-3 gap-y-1 px-4 py-2 text-[11px] text-subtle bg-background/80 backdrop-blur-sm border-t border-border/50">
      <span>&copy; {new Date().getFullYear()} utictactoe</span>
      <span className="hidden sm:inline">&middot;</span>
      <span className="hidden sm:inline">Built by{" "}
        <a href="https://www.linkedin.com/in/manuel-delpino/" target="_blank" rel="noopener noreferrer" className="hover:text-muted-foreground transition-colors">Manuel Delpino</a>
        {" & "}
        <a href="https://www.linkedin.com/in/manuel-meiri%C3%B1o-7b9214331/" target="_blank" rel="noopener noreferrer" className="hover:text-muted-foreground transition-colors">Manuel Meiriño</a>
      </span>
      <span>&middot;</span>
      <Link href="/privacy-policy" className="hover:text-muted-foreground transition-colors">Privacy</Link>
      <span>&middot;</span>
      <Link href="/terms-of-service" className="hover:text-muted-foreground transition-colors">Terms</Link>
    </footer>
    </>
  );
}
