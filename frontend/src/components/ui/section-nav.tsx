"use client";
import { useEffect, useState } from "react";
import { Target, BookOpen, Trophy, Lightbulb, Zap, MousePointer, AlertTriangle, HelpCircle, Cpu, Shield, Database, Share2, Lock, Baby, RefreshCw, Mail, FileText, Gamepad2, Code2, UserCheck, Scale } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const ICON_MAP: Record<string, LucideIcon> = {
  Target, BookOpen, Trophy, Lightbulb, Zap, MousePointer, AlertTriangle,
  HelpCircle, Cpu, Shield, Database, Share2, Lock, Baby, RefreshCw, Mail,
  FileText, Gamepad2, Code2, UserCheck, Scale,
};

interface Section {
  id: string;
  title: string;
  icon: string; // icon name key
}

export default function SectionNav({ sections }: { sections: Section[] }) {
  const [active, setActive] = useState(sections[0]?.id ?? "");

  useEffect(() => {
    const observers: IntersectionObserver[] = [];
    sections.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (!el) return;
      const obs = new IntersectionObserver(
        ([entry]) => { if (entry.isIntersecting) setActive(id); },
        { rootMargin: "-30% 0px -60% 0px", threshold: 0 }
      );
      obs.observe(el);
      observers.push(obs);
    });
    return () => observers.forEach(o => o.disconnect());
  }, [sections]);

  return (
    <>
      {/* Desktop sticky sidebar */}
      <aside className="hidden md:flex flex-col gap-1 w-44 shrink-0">
        <div className="sticky top-20">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground mb-3 px-2">On this page</p>
          {sections.map(({ id, title, icon }) => {
            const Icon = ICON_MAP[icon];
            const isActive = active === id;
            return (
              <a
                key={id}
                href={`#${id}`}
                className={`flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm transition-colors ${
                  isActive ? "bg-surface text-foreground font-medium" : "text-muted-foreground hover:text-foreground hover:bg-surface"
                }`}
              >
                {Icon && <Icon className={`w-3.5 h-3.5 shrink-0 ${isActive ? "text-foreground" : ""}`} />}
                {title}
              </a>
            );
          })}
        </div>
      </aside>

      {/* Mobile pill nav */}
      <div className="md:hidden flex flex-wrap gap-2 mb-8 w-full">
        {sections.map(({ id, title }) => (
          <a
            key={id}
            href={`#${id}`}
            className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
              active === id ? "bg-surface text-foreground font-medium" : "bg-surface text-muted-foreground hover:text-foreground"
            }`}
          >
            {title}
          </a>
        ))}
      </div>
    </>
  );
}
