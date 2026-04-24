import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Play",
  description: "Choose your game mode and start playing Ultimate Tic-Tac-Toe.",
};

export default function PlayLayout({ children }: { children: React.ReactNode }) {
  return children;
}
