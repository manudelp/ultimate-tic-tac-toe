"use client";
import { useEffect, useRef, useMemo, useState } from "react";
import Link from "next/link";
import { Bot, Globe, Users, MousePointerClick, ArrowRight, Shuffle, Trophy } from "lucide-react";
import HeroBoard from "@/components/core/hero-board";
import ThemeToggle from "@/components/ui/theme-toggle";
import { motion, Variants } from "framer-motion";

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

const fadeDown: Variants = {
  hidden: { opacity: 0, y: -16 },
  visible: { opacity: 1, y: 0 },
};

const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: { opacity: 1, scale: 1 },
};

const fadeLeft: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

const fadeRight: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0 },
};

const stagger: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

const staggerFast: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.07 } },
};

const staggerSlow: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.15 } },
};

const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

const WORDS = [
  "strategy", "skill", "tactics", "planning", "execution",
  "decision-making", "wit", "adaptability", "foresight", "precision",
];

const COLORS = [
  "#60a5fa", "#f87171", "#34d399", "#a78bfa", "#fbbf24",
  "#38bdf8", "#fb923c", "#4ade80", "#e879f9", "#f472b6",
];

const STEPS = [
  {
    icon: MousePointerClick,
    num: "01",
    title: "Pick a cell",
    desc: "Play your mark in any available mini-board to start your turn.",
  },
  {
    icon: ArrowRight,
    num: "02",
    title: "Direct your opponent",
    desc: "The cell you pick determines which mini-board your opponent must play in next.",
  },
  {
    icon: Trophy,
    num: "03",
    title: "Win the big board",
    desc: "Claim three mini-boards in a row — horizontally, vertically, or diagonally.",
  },
];

const MODES = [
  {
    icon: Bot,
    title: "vs AI",
    desc: "From casual to expert difficulty. Train your skills against increasingly smart bots.",
    cta: "Challenge a bot",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    icon: Globe,
    title: "Online",
    desc: "Jump into matchmaking or create a private lobby and share the code with a friend.",
    cta: "Play online",
    color: "text-green-400",
    bg: "bg-green-500/10",
  },
  {
    icon: Users,
    title: "Local",
    desc: "Pass and play on the same device. Perfect for a quick game with someone next to you.",
    cta: "Play locally",
    color: "text-purple-400",
    bg: "bg-purple-500/10",
  },
];

const FEATURES = [
  {
    icon: Shuffle,
    title: "Forced moves",
    desc: "Every move you make sends your opponent to a specific board — control the game by thinking two steps ahead.",
  },
  {
    icon: Bot,
    title: "AI opponents",
    desc: "A range of opponents from beginner-friendly to genuinely challenging. There's always a worthy match."
  },
  {
    icon: Globe,
    title: "Real-time multiplayer",
    desc: "Real-time online play with no lag. Jump into matchmaking or create a private lobby with a shareable code.",
  },
  {
    icon: Trophy,
    title: "Move history & analysis",
    desc: "Every game records a full move log with timestamps and an advantage bar so you can review your decisions.",
  },
];

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [boardReady, setBoardReady] = useState(false);
  const typeRef = useRef<HTMLSpanElement>(null);
  const shuffledWords = useMemo(() => shuffleArray(WORDS), []);
  const shuffledColors = useMemo(() => shuffleArray(COLORS), []);

  useEffect(() => {
    if (!typeRef.current) return;
    let wordIndex = 0, charIndex = 0, isDeleting = false, frame: number;

    const tick = () => {
      const word = shuffledWords[wordIndex];
      if (typeRef.current) {
        typeRef.current.textContent = isDeleting
          ? word.substring(0, charIndex--)
          : word.substring(0, charIndex++);
        typeRef.current.style.color = shuffledColors[wordIndex];
      }
      if (!isDeleting && charIndex === word.length + 1) {
        setTimeout(() => { isDeleting = true; frame = requestAnimationFrame(tick); }, 1200);
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        wordIndex = (wordIndex + 1) % shuffledWords.length;
        frame = requestAnimationFrame(tick);
      } else {
        setTimeout(() => { frame = requestAnimationFrame(tick); }, isDeleting ? 45 : 90);
      }
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [shuffledWords, shuffledColors]);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="flex flex-col">

      {/* ── Hero ── */}
      <section className="relative min-h-[85vh] sm:min-h-[90vh] flex flex-col overflow-hidden">
        <nav className="flex items-center justify-between px-4 sm:px-8 h-14 shrink-0">
          <span className="text-base font-extrabold tracking-tight text-foreground">utictactoe</span>
          <div className="flex items-center gap-2 sm:gap-4">
            <Link href="/learn" className="text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors">
              How to Play
            </Link>
            <Link href="/play" className="text-xs sm:text-sm px-3 sm:px-4 py-1.5 border border-border rounded-md font-medium text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors">
              Play
            </Link>
            <ThemeToggle />
          </div>
        </nav>

        <motion.div
          className={`flex-1 flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 px-6 sm:px-12 pb-10 sm:pb-16 pt-8 ${mounted && boardReady ? "" : "opacity-0"}`}
          initial="hidden"
          animate={mounted && boardReady ? "visible" : "hidden"}
          variants={stagger}
        >
          <motion.div
            className="flex flex-col items-center md:items-start text-center md:text-left max-w-[680px]"
            variants={stagger}
          >
            <motion.h1 variants={fadeDown} transition={{ duration: 0.6, ease: "easeOut" }} className="text-3xl sm:text-4xl md:text-6xl font-bold tracking-tight leading-[1.1] mb-4">
              Ultimate<br />
              <span className="text-muted-foreground">Tic-Tac-Toe.</span>
            </motion.h1>
            <motion.p variants={fadeUp} transition={{ duration: 0.5 }} className="text-muted-foreground/80 text-base sm:text-lg mb-2 leading-relaxed max-w-md">
              A game of <span ref={typeRef} className="font-semibold" />.
            </motion.p>
            <motion.p variants={fadeUp} transition={{ duration: 0.5 }} className="text-muted-foreground/70 text-sm sm:text-base mb-8 leading-[1.7] max-w-lg">
              Nine boards. Every move you make sends your opponent somewhere specific.
              Think ahead or lose control.
            </motion.p>
            <motion.div variants={fadeUp} transition={{ duration: 0.5 }} className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
              <Link
                href="/play"
                className="w-full sm:w-auto px-8 py-3 bg-green-600 hover:bg-green-500 text-white font-semibold rounded-lg transition-colors text-sm text-center"
              >
                Play Now — it&apos;s free
              </Link>
              <Link
                href="/learn"
                className="w-full sm:w-auto px-6 py-3 text-sm text-muted-foreground hover:text-foreground border border-transparent hover:border-border rounded-lg transition-colors text-center"
              >
                Learn the rules →
              </Link>
            </motion.div>
            <motion.p variants={fadeUp} transition={{ duration: 0.5 }} className="text-xs text-muted-foreground/50 mt-4">No account needed · Free · Instant play</motion.p>
          </motion.div>

          <motion.div
            variants={scaleIn}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center justify-center w-[280px] h-[280px] md:w-[400px] md:h-[400px] shrink-0"
          >
            <HeroBoard onReady={() => setBoardReady(true)} />
          </motion.div>
        </motion.div>
      </section>

      {/* ── How it works ── */}
      <motion.section
        className="px-6 sm:px-12 py-14 sm:py-24 border-t border-border/50"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={staggerSlow}
      >
        <div className="max-w-4xl mx-auto">
          <motion.div variants={fadeUp} transition={{ duration: 0.5 }} className="text-center mb-8 sm:mb-16">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2 sm:mb-3">How it works</p>
            <h2 className="text-2xl sm:text-3xl font-bold">Three steps to victory</h2>
          </motion.div>
          <motion.div className="grid gap-3 sm:gap-8 sm:grid-cols-3" variants={staggerSlow}>
            {STEPS.map((s, i) => (
              <motion.div
                key={s.num}
                variants={i === 0 ? fadeLeft : i === 2 ? fadeRight : fadeUp}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="relative flex flex-col gap-3 sm:gap-4 p-4 sm:p-6 rounded-xl border border-border/50 bg-background"
              >
                <span className="text-[11px] font-bold text-muted-foreground/50 tracking-widest">{s.num}</span>
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <s.icon className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">{s.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* ── Game modes ── */}
      <motion.section
        className="px-6 sm:px-12 py-14 sm:py-24 border-t border-border/50"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={staggerFast}
      >
        <div className="max-w-4xl mx-auto">
          <motion.div variants={fadeDown} transition={{ duration: 0.4 }} className="text-center mb-8 sm:mb-16">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2 sm:mb-3">Game modes</p>
            <h2 className="text-2xl sm:text-3xl font-bold">Play your way</h2>
          </motion.div>
          <motion.div className="grid gap-3 sm:gap-4 sm:grid-cols-3" variants={staggerFast}>
            {MODES.map(({ icon: Icon, title, desc, cta, color, bg }) => (
              <motion.div
                key={title}
                variants={scaleIn}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                className="group flex flex-col gap-3 sm:gap-4 p-4 sm:p-6 rounded-xl border border-border/50 bg-background hover:border-border transition-colors"
              >
                <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-1 sm:mb-2">{title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                </div>
                <Link
                  href="/play"
                  className={`text-xs font-medium ${color} flex items-center gap-1 group-hover:gap-2 transition-all`}
                >
                  {cta} <ArrowRight className="w-3 h-3" />
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* ── Features ── */}
      <motion.section
        className="px-6 sm:px-12 py-14 sm:py-24 border-t border-border/50"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.15 }}
        variants={stagger}
      >
        <div className="max-w-4xl mx-auto">
          <motion.div variants={fadeUp} transition={{ duration: 0.5 }} className="text-center mb-8 sm:mb-16">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2 sm:mb-3">Features</p>
            <h2 className="text-2xl sm:text-3xl font-bold">Everything you need</h2>
          </motion.div>
          <motion.div className="grid gap-3 sm:gap-4 sm:grid-cols-2" variants={stagger}>
            {FEATURES.map(({ icon: Icon, title, desc }, i) => (
              <motion.div
                key={title}
                variants={i % 2 === 0 ? fadeLeft : fadeRight}
                transition={{ duration: 0.45, ease: "easeOut" }}
                className="flex gap-3 sm:gap-4 p-4 sm:p-6 rounded-xl border border-border/50 bg-background"
              >
                <div className="w-9 h-9 rounded-lg bg-surface shrink-0 flex items-center justify-center mt-0.5">
                  <Icon className="w-4 h-4 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1 text-sm">{title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* ── CTA ── */}
      <motion.section
        className="px-6 sm:px-12 py-14 sm:py-24 border-t border-border/50"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.3 }}
        variants={stagger}
      >
        <motion.div variants={scaleIn} transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }} className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 sm:mb-4">Ready to play?</h2>
          <p className="text-muted-foreground mb-6 sm:mb-8 text-sm sm:text-base leading-relaxed">
            No account needed. No downloads. Jump straight into a game in seconds.
          </p>
          <Link
            href="/play"
            className="inline-flex items-center gap-2 px-8 sm:px-10 py-3 sm:py-3.5 bg-green-600 hover:bg-green-500 text-white text-sm sm:text-base font-semibold rounded-lg transition-colors"
          >
            Start Playing <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>
      </motion.section>

      {/* ── Footer ── */}
      <footer className="border-t border-border/50 flex flex-col sm:flex-row items-center justify-between gap-2 sm:gap-3 px-6 sm:px-12 py-4 sm:py-6 text-[11px] text-subtle">
        <span className="font-semibold text-muted-foreground">utictactoe</span>
        <div className="flex items-center flex-wrap justify-center gap-x-3 gap-y-1">
          <span>&copy; {new Date().getFullYear()}</span>
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
        </div>
      </footer>
    </div>
  );
}
