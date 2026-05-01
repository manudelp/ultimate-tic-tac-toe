"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Sun, Moon, Monitor } from "lucide-react";

const cycle = ["light", "dark", "system"] as const;
const icons = { light: Sun, dark: Moon, system: Monitor };
const labels = { light: "Light", dark: "Dark", system: "System" };

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return <div className="w-8 h-8" />;

  const current = (cycle.includes(theme as any) ? theme : "system") as (typeof cycle)[number];
  const next = cycle[(cycle.indexOf(current) + 1) % cycle.length];
  const Icon = icons[current];

  return (
    <button
      onClick={() => setTheme(next)}
      className="flex items-center justify-center w-8 h-8 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
      aria-label={`Theme: ${labels[current]}. Switch to ${labels[next]}`}
      title={`${labels[current]} theme`}
    >
      <Icon className="w-4 h-4" />
    </button>
  );
}
