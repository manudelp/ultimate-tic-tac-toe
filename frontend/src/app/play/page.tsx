"use client";
import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getBots, getQueueCounts } from "@/api";
import { toastInvalidLobbyCode } from "@/lib/toasts";
import { Bot, Globe, Users, Swords, Clock, ArrowRight, Link2, Hash, ChevronLeft, RotateCcw, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import Loader from "@/components/ui/loader";
import type { BotInfo } from "@/types/game";

type Tab = "ai" | "online" | "local";

const TABS: { id: Tab; label: string; icon: React.ElementType; desc: string }[] = [
  { id: "ai",     label: "vs AI",   icon: Bot,   desc: "Challenge a bot" },
  { id: "online", label: "Online",  icon: Globe,  desc: "Play globally" },
  { id: "local",  label: "Local",   icon: Users,  desc: "Same device" },
];

const TIME_OPTIONS: { label: string; value: number | null }[] = [
  { label: "1 min",    value: 60 },
  { label: "3 min",    value: 180 },
  { label: "5 min",    value: 300 },
  { label: "10 min",   value: 600 },
  { label: "No limit", value: null },
];

function SegmentedControl({
  options,
  value,
  onChange,
  id,
}: {
  options: { label: string; value: string | number | null }[];
  value: string | number | null;
  onChange: (v: string | number | null) => void;
  id: string;
}) {
  return (
    <div className="flex bg-surface rounded-lg p-0.5 gap-0.5 w-full">
      {options.map((opt) => (
        <button
          key={opt.label}
          onClick={() => onChange(opt.value)}
          className="relative flex-1 min-w-0 px-1.5 sm:px-3 py-2 text-[11px] sm:text-xs font-medium rounded-md transition-colors"
        >
          {value === opt.value && (
            <motion.div
              layoutId={id}
              className="absolute inset-0 bg-background rounded-md shadow-sm"
              transition={{ type: "spring", stiffness: 400, damping: 35 }}
            />
          )}
          <span className={`relative z-10 transition-colors truncate block ${
            value === opt.value ? "text-foreground" : "text-muted-foreground"
          }`}>
            {opt.label}
          </span>
        </button>
      ))}
    </div>
  );
}

export default function Play() {
  return (
    <Suspense>
      <PlayContent />
    </Suspense>
  );
}

function PlayContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState<Tab>("ai");

  useEffect(() => {
    const joinCode = searchParams.get("join");
    if (joinCode) {
      sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", lobbyCode: joinCode.toUpperCase() }));
      router.replace("/game");
    }
  }, [searchParams, router]);

  const [bots, setBots] = useState<BotInfo[] | null>(null);
  const [selectedBot, setSelectedBot] = useState<BotInfo | null>(null);
  const [starts, setStarts] = useState<string | null>("player");
  const [timeControl, setTimeControl] = useState<number | null>(300);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [lobbyInput, setLobbyInput] = useState("");
  const [queueCounts, setQueueCounts] = useState<Record<string, number>>({});
  const [resumeData, setResumeData] = useState<{ opponent?: { icon: string; name: string }; isLocal?: boolean } | null>(null);

  // Check for active game to rejoin
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("uttt_resume");
      if (raw) {
        const data = JSON.parse(raw);
        setResumeData({ opponent: data.opponent, isLocal: data.isLocal });
      }
    } catch {
      sessionStorage.removeItem("uttt_resume");
    }
  }, []);

  useEffect(() => {
    if (tab !== "online") return;
    const fetchCounts = () => getQueueCounts().then(setQueueCounts).catch(() => {});
    fetchCounts();
    const interval = setInterval(fetchCounts, 5000);
    return () => clearInterval(interval);
  }, [tab]);

  useEffect(() => {
    if (tab === "ai" && !bots) {
      setLoading(true);
      setError(false);
      getBots()
        .then((data) => { setBots(data); setLoading(false); })
        .catch(() => { setLoading(false); setError(true); });
    }
  }, [tab, bots]);

  const startAIGame = () => {
    if (!selectedBot || !starts) return;
    sessionStorage.setItem("uttt_game_config", JSON.stringify({
      mode: "player-vs-bot", botId: selectedBot.id, bot: selectedBot, starts, timeControl: null,
    }));
    router.push("/game");
  };

  const startLocalGame = () => {
    sessionStorage.setItem("uttt_game_config", JSON.stringify({
      mode: "player-vs-player", starts: starts || "player", timeControl,
    }));
    router.push("/game");
  };

  const joinLobby = () => {
    const code = lobbyInput.trim().toUpperCase();
    if (code.length === 4) {
      sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", lobbyCode: code }));
      router.push("/game");
    } else {
      toastInvalidLobbyCode();
    }
  };

  const createLobby = () => {
    sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", timeControl }));
    router.push("/game");
  };

  const quickMatch = () => {
    sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", matchmaking: true, timeControl }));
    router.push("/game");
  };

  const queueKey = timeControl === null ? "null" : String(timeControl);
  const queueCount = queueCounts[queueKey] || 0;

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-8 pt-4 pb-8 sm:py-12">

      {/* Header */}
      <div className="mb-8 sm:mb-10">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">Play</p>
        <h1 className="text-2xl sm:text-4xl font-bold tracking-tight mb-2">Choose your game</h1>
        <p className="text-muted-foreground text-sm sm:text-base leading-relaxed">
          Pick a mode and jump straight in. No account needed.
        </p>
      </div>

      {/* Rejoin banner */}
      {resumeData && (
        <div className="mb-6 sm:mb-8 p-4 rounded-xl border border-yellow-500/30 bg-yellow-500/5 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-yellow-500/10 flex items-center justify-center shrink-0">
              <RotateCcw className="w-4 h-4 text-yellow-400" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold">Game in progress</p>
              <p className="text-xs text-muted-foreground truncate">
                {resumeData.opponent ? `vs ${resumeData.opponent.icon} ${resumeData.opponent.name}` : resumeData.isLocal ? "Local game" : "Online game"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => {
                sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "rejoin" }));
                router.push("/game");
              }}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 text-white text-xs font-bold rounded-lg transition-colors"
            >
              Rejoin
            </button>
            <button
              onClick={() => {
                sessionStorage.removeItem("uttt_resume");
                setResumeData(null);
              }}
              className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Tab selector */}
      <div className="grid grid-cols-3 gap-2 sm:gap-3 mb-6 sm:mb-8">
        {TABS.map(({ id, label, icon: Icon, desc }) => (
          <button
            key={id}
            onClick={() => { setTab(id); setSelectedBot(null); setStarts("player"); }}
            className={`flex flex-col items-center sm:items-start gap-1.5 sm:gap-2 p-3 sm:p-4 rounded-xl border transition-all text-center sm:text-left ${
              tab === id
                ? "border-border bg-background shadow-sm"
                : "border-border/50 bg-background hover:border-border text-muted-foreground"
            }`}
          >
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
              tab === id ? "bg-blue-500/10" : "bg-surface"
            }`}>
              <Icon className={`w-4 h-4 ${tab === id ? "text-blue-400" : "text-muted-foreground"}`} />
            </div>
            <div>
              <p className={`text-sm font-semibold ${tab === id ? "text-foreground" : ""}`}>{label}</p>
              <p className="text-[11px] text-muted-foreground hidden sm:block">{desc}</p>
            </div>
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div>
        <AnimatePresence mode="wait">

          {/* ── vs AI ── */}
          {tab === "ai" && (
            <motion.div
              key="ai"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
            >
              {loading ? (
                <div className="flex flex-col items-center justify-center py-16 gap-4">
                  <Loader />
                  <p className="text-sm text-muted-foreground">Loading AI opponents...</p>
                </div>
              ) : error ? (
                <div className="flex flex-col items-center justify-center py-16 gap-3">
                  <p className="text-sm font-medium text-red-400">Failed to load AI opponents</p>
                  <button onClick={() => setBots(null)} className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                    Try again
                  </button>
                </div>
              ) : (
                <AnimatePresence mode="wait">
                  {!selectedBot ? (
                    <motion.div
                      key="grid"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.12 }}
                      className="space-y-3"
                    >
                      <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Select your opponent</p>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
                        {bots?.sort((a, b) => a.difficulty - b.difficulty).map((bot) => (
                          <button
                            key={bot.id}
                            onClick={() => setSelectedBot(bot)}
                            className="flex flex-col items-center gap-2 p-4 sm:p-4 rounded-xl border border-border/50 bg-background hover:border-border transition-all group"
                          >
                            <span className="text-4xl sm:text-5xl leading-none group-hover:scale-110 transition-transform">{bot.icon}</span>
                            <span className="text-xs font-semibold text-muted-foreground group-hover:text-foreground transition-colors">{bot.name}</span>
                            <div className="flex gap-1">
                              {Array(5).fill(0).map((_, i) => (
                                <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < bot.difficulty ? "bg-green-500" : "bg-border"}`} />
                              ))}
                            </div>
                          </button>
                        ))}
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key={`selected-${selectedBot.id}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.12 }}
                      className="space-y-3"
                    >
                      {/* Back to grid */}
                      <button
                        onClick={() => setSelectedBot(null)}
                        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors mb-1"
                      >
                        <ChevronLeft className="w-3.5 h-3.5" /> All opponents
                      </button>

                      {/* Bot detail card */}
                      <div className="flex flex-col gap-4 p-4 rounded-xl border border-border/50 bg-background">
                        <div className="flex items-start gap-3 pb-3 border-b border-border/40">
                          <span className="text-3xl leading-none">{selectedBot.icon}</span>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold">{selectedBot.name}</p>
                            <p className="text-xs text-muted-foreground leading-snug mt-0.5">{selectedBot.description}</p>
                          </div>
                          <div className="flex gap-0.5 pt-1 shrink-0">
                            {Array(5).fill(0).map((_, i) => (
                              <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < selectedBot.difficulty ? "bg-green-500" : "bg-border"}`} />
                            ))}
                          </div>
                        </div>

                        <div className="flex items-center justify-between gap-4">
                          <span className="text-xs text-muted-foreground whitespace-nowrap">First move</span>
                          <SegmentedControl
                            id="ai-starts"
                            options={[{ label: "You", value: "player" }, { label: "Opponent", value: "bot" }]}
                            value={starts}
                            onChange={(v) => setStarts(v as string)}
                          />
                        </div>

                        <button
                          disabled={!starts}
                          onClick={startAIGame}
                          className="w-full py-3 bg-green-600 hover:bg-green-500 disabled:opacity-30 disabled:cursor-not-allowed text-white text-sm font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                          <Swords className="w-4 h-4" />
                          Fight!
                        </button>
                      </div>

                      {/* Quick-switch roster */}
                      <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin scrollbar-thumb-muted">
                        {bots?.sort((a, b) => a.difficulty - b.difficulty).map((bot) => {
                          const isSelected = selectedBot?.id === bot.id;
                          return (
                            <button
                              key={bot.id}
                              onClick={() => setSelectedBot(bot)}
                              className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors shrink-0 ${
                                isSelected ? "border-border bg-surface" : "border-border/50 bg-background hover:border-border"
                              }`}
                            >
                              <span className="text-lg leading-none">{bot.icon}</span>
                              <span className={`text-xs font-semibold ${isSelected ? "text-foreground" : "text-muted-foreground"}`}>
                                {bot.name}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              )}
            </motion.div>
          )}

          {/* ── Online ── */}
          {tab === "online" && (
            <motion.div
              key="online"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
              className="space-y-3"
            >
              {/* Time control */}
              <div className="p-4 rounded-xl border border-border/50 bg-background space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Time control</span>
                  </div>
                  {queueCount > 0 && (
                    <span className="text-[11px] text-green-400 font-medium">
                      {queueCount} searching
                    </span>
                  )}
                </div>
                <SegmentedControl
                  id="online-time"
                  options={TIME_OPTIONS}
                  value={timeControl}
                  onChange={(v) => setTimeControl(v as number | null)}
                />
              </div>

              {/* Quick match */}
              <div className="p-4 rounded-xl border border-border/50 bg-background space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center shrink-0">
                    <Globe className="w-4 h-4 text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">Quick Match</p>
                    <p className="text-xs text-muted-foreground">Find a random opponent instantly</p>
                  </div>
                </div>
                <button
                  onClick={quickMatch}
                  className="w-full py-3 bg-green-600 hover:bg-green-500 text-white text-sm font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <ArrowRight className="w-4 h-4" />
                  Find Opponent
                </button>
              </div>

              {/* Private lobby */}
              <div className="p-4 rounded-xl border border-border/50 bg-background space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                    <Link2 className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">Private Lobby</p>
                    <p className="text-xs text-muted-foreground">Play with a friend using a code</p>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-2">
                  <button
                    onClick={createLobby}
                    className="w-full sm:flex-1 py-2.5 bg-surface hover:bg-surface-hover rounded-lg text-xs font-medium transition-colors"
                  >
                    Create Lobby
                  </button>
                  <div className="flex gap-1.5 w-full sm:flex-1">
                    <input
                      type="text"
                      value={lobbyInput}
                      onChange={(e) => setLobbyInput(e.target.value.toUpperCase())}
                      onKeyDown={(e) => e.key === "Enter" && joinLobby()}
                      placeholder="CODE"
                      maxLength={4}
                      className="flex-1 min-w-0 px-3 py-2.5 bg-surface border border-border/50 rounded-lg text-xs font-mono tracking-widest text-center focus:outline-none focus:border-ring transition-colors"
                    />
                    <button
                      onClick={joinLobby}
                      className="px-4 py-2.5 bg-surface hover:bg-surface-hover rounded-lg text-xs font-medium transition-colors"
                    >
                      Join
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* ── Local ── */}
          {tab === "local" && (
            <motion.div
              key="local"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
            >
              <div className="p-4 sm:p-6 rounded-xl border border-border/50 bg-background space-y-5">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-purple-500/10 flex items-center justify-center shrink-0">
                    <Users className="w-4 h-4 text-purple-400" />
                  </div>
                  <div>
                    <p className="font-semibold">Local Game</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Pass and play on the same device</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Hash className="w-3.5 h-3.5 text-muted-foreground" />
                      <span className="text-xs sm:text-sm text-muted-foreground">First move</span>
                    </div>
                    <SegmentedControl
                      id="local-starts"
                      options={[{ label: "Player X", value: "player" }, { label: "Player O", value: "playerO" }]}
                      value={starts}
                      onChange={(v) => setStarts(v as string)}
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                      <span className="text-xs sm:text-sm text-muted-foreground">Time control</span>
                    </div>
                    <SegmentedControl
                      id="local-time"
                      options={TIME_OPTIONS}
                      value={timeControl}
                      onChange={(v) => setTimeControl(v as number | null)}
                    />
                  </div>
                </div>

                <button
                  onClick={startLocalGame}
                  className="w-full py-3 bg-green-600 hover:bg-green-500 text-white text-sm font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Users className="w-4 h-4" />
                  Start Game
                </button>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
