import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Learn",
  description: "Learn the rules, strategies, and tips for Ultimate Tic-Tac-Toe.",
};

export default function LearnLayout({ children }: { children: React.ReactNode }) {
  return children;
}
