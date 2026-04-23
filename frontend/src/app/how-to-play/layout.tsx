import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "How to Play",
  description:
    "Learn the rules, strategies, and tips for Ultimate Tic Tac Toe.",
};

export default function HowToPlayLayout({ children }: { children: React.ReactNode }) {
  return children;
}
