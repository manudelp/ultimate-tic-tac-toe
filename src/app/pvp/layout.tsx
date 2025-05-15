import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Epic 1v1 Showdown - Ultimate Tic Tac Toe",
  description:
    "Challenge a friend in the ultimate battle of wits and strategy! Play locally or connect online for an epic tactical duel.",
};

export default function PVPLayout({ children }: { children: React.ReactNode }) {
  return children;
}
