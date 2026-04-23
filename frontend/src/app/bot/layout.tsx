import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Play vs AI",
  description:
    "Challenge AI opponents with different difficulty levels and strategies.",
};

export default function BotLayout({ children }: { children: React.ReactNode }) {
  return children;
}
