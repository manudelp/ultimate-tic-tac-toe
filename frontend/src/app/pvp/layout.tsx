import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Play vs Player",
  description:
    "Challenge a friend locally or connect online for a strategic duel.",
};

export default function PVPLayout({ children }: { children: React.ReactNode }) {
  return children;
}
