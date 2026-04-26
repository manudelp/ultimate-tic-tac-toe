"use client";
import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getBots, getQueueCounts } from "@/api";
import { toast } from "sonner";
import { Bot, Globe, Users, Swords, Clock } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import Loader from "@/components/ui/loader";
import type { BotInfo } from "@/types/game";

type Tab = "ai" | "online" | "local";

const TABS: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: "ai", label: "vs AI", icon: Bot },
  { id: "online", label: "Online", icon: Globe },
  { id: "local", label: "Local", icon: Users },
];

const TIME_OPTIONS: { label: string; value: number | null }[] = [
  { label: "1 min", value: 60 },
  { label: "3 min", value: 180 },
  { label: "5 min", value: 300 },
  { label: "10 min", value: 600 },
  { label: "No limit", value: null },
];

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

  // Handle ?join= query param
  useEffect(() => {
    const joinCode = searchParams.get("join");
    if (joinCode) {
      sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", lobbyCode: joinCode.toUpperCase() }));
      router.replace("/game");
    }
  }, [searchParams, router]);

  // AI state
  const [bots, setBots] = useState<BotInfo[] | null>(null);
  const [selectedBot, setSelectedBot] = useState<BotInfo | null>(null);
  const [starts, setStarts] = useState<string | null>("player");
  const [timeControl, setTimeControl] = useState<number | null>(300);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Online state
  const [lobbyInput, setLobbyInput] = useState("");
  const [queueCounts, setQueueCounts] = useState<Record<string, number>>({});

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
        .then((data) => {
          setBots(data);
          setLoading(false);
        })
        .catch(() => { setLoading(false); setError(true); });
    }
  }, [tab, bots]);

  const startAIGame = () => {
    if (!selectedBot || !starts) return;
    sessionStorage.setItem("uttt_game_config", JSON.stringify({
      mode: "player-vs-bot", botId: selectedBot.id, bot: selectedBot, starts, timeControl,
    }));
    router.push("/game");
  };

  const startLocalGame = (who: string) => {
    sessionStorage.setItem("uttt_game_config", JSON.stringify({
      mode: "player-vs-player", starts: who, timeControl,
    }));
    router.push("/game");
  };

  const joinLobby = () => {
    const code = lobbyInput.trim().toUpperCase();
    if (code.length === 4) {
      sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", lobbyCode: code }));
      router.push("/game");
    } else {
      toast.error("Enter a valid 4-character lobby code.");
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

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100svh-3.5rem)] px-4 py-8">
      {/* Hero */}
      <h1 className="text-3xl sm:text-4xl font-bold mb-2 tracking-tight">Play Ultimate Tic-Tac-Toe</h1>
      <p className="text-gray-400 mb-8 text-sm sm:text-base">Choose your game mode</p>

      {/* Tabs */}
      <div className="flex bg-gray-800 rounded-lg p-1 mb-8">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => { setTab(id); setSelectedBot(null); setStarts("player"); }}
            className={`flex items-center gap-2 px-5 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === id ? "bg-gray-700 text-white" : "text-gray-400 hover:text-white"
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="w-full max-w-lg min-h-[360px]">
        {/* ── vs AI ── */}
        {tab === "ai" && (
          <div>
            {loading ? (
              <div className="flex flex-col items-center py-12">
                <Loader />
                <p className="mt-4 text-sm text-gray-400">Loading AI opponents...</p>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center py-12">
                <p className="text-red-400 font-medium mb-2">Failed to load AI opponents</p>
                <button onClick={() => setBots(null)} className="text-sm text-blue-400 hover:text-blue-300">Retry</button>
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
                    className="space-y-5"
                  >
                    <p className="text-center text-sm text-gray-500 uppercase tracking-widest">Select your opponent</p>
                    <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
                      {bots?.sort((a, b) => a.difficulty - b.difficulty).map((bot) => (
                        <button
                          key={bot.id}
                          onClick={() => { setSelectedBot(bot); }}
                          className="relative flex flex-col items-center gap-1.5 p-3 sm:p-4 rounded-xl border border-gray-700/50 bg-gray-800/40 hover:border-gray-600 transition-colors w-[calc(25%-0.5rem)] sm:w-[calc(25%-0.75rem)] min-w-[75px]"
                        >
                          <span className="text-4xl sm:text-5xl leading-none">{bot.icon}</span>
                          <span className="text-xs sm:text-sm font-semibold text-gray-300">{bot.name}</span>
                          <div className="flex gap-0.5">
                            {Array(5).fill(0).map((_, i) => (
                              <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < bot.difficulty ? "bg-gray-400" : "bg-gray-700"}`} />
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
                  >
                    <div className="flex gap-3">
                      {/* Roster (left) — scrollable */}
                      <div className="flex flex-col gap-1.5 max-h-[340px] overflow-y-auto pr-0.5">
                        {bots?.sort((a, b) => a.difficulty - b.difficulty).map((bot) => {
                          const selected = selectedBot?.id === bot.id;
                          return (
                            <button
                              key={bot.id}
                              onClick={() => { setSelectedBot(selected ? null : bot); }}
                              className={`flex items-center gap-2 px-2.5 py-2 rounded-lg border transition-colors w-[120px] shrink-0 ${
                                selected
                                  ? "border-gray-500/50 bg-gray-700/50"
                                  : "border-gray-700/50 bg-gray-800/40 hover:border-gray-600"
                              }`}
                            >
                              <span className="text-lg leading-none">{bot.icon}</span>
                              <div className="flex flex-col items-start min-w-0">
                                <span className={`text-xs font-semibold truncate ${
                                  selected ? "text-white" : "text-gray-400"
                                }`}>{bot.name}</span>
                                <div className="flex gap-0.5">
                                  {Array(5).fill(0).map((_, i) => (
                                    <div key={i} className={`w-1 h-1 rounded-full ${i < bot.difficulty ? "bg-gray-400" : "bg-gray-700"}`} />
                                  ))}
                                </div>
                              </div>
                            </button>
                          );
                        })}
                      </div>

                      {/* Detail (right) */}
                      <div className="flex-1 min-w-0">
                        <AnimatePresence mode="wait">
                          <motion.div
                            key={selectedBot.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.12 }}
                            className="flex flex-col justify-between p-4 rounded-xl border border-gray-700/50 bg-gray-800/40 h-full"
                          >
                            {/* Header */}
                            <div className="flex items-start gap-3 pb-3 border-b border-gray-700/40">
                              <span className="text-2xl">{selectedBot.icon}</span>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-bold text-gray-200">{selectedBot.name}</p>
                                <p className="text-[11px] text-gray-500 leading-snug mt-0.5">{selectedBot.description}</p>
                              </div>
                              <div className="flex gap-0.5 pt-1.5 shrink-0">
                                {Array(5).fill(0).map((_, i) => (
                                  <div key={i} className={`w-1 h-1 rounded-full ${i < selectedBot.difficulty ? "bg-gray-400" : "bg-gray-700"}`} />
                                ))}
                              </div>
                            </div>

                            {/* Settings */}
                            <div className="flex flex-col gap-3 py-3">
                              <div className="flex items-center justify-between">
                                <span className="text-[11px] text-gray-500 uppercase tracking-wider">First move</span>
                                <div className="flex bg-gray-800 rounded-md p-0.5">
                                  {(["player", "bot"] as const).map((v) => (
                                    <button
                                      key={v}
                                      onClick={() => setStarts(v)}
                                      className={`px-3 py-1 text-[11px] font-medium rounded transition-all ${
                                        starts === v
                                          ? "bg-gray-700 text-white"
                                          : "text-gray-500 hover:text-gray-300"
                                      }`}
                                    >
                                      {v === "player" ? "You" : "Opponent"}
                                    </button>
                                  ))}
                                </div>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-[11px] text-gray-500 uppercase tracking-wider">Time</span>
                                <div className="flex bg-gray-800 rounded-md p-0.5">
                                  {TIME_OPTIONS.map((opt) => (
                                    <button
                                      key={opt.label}
                                      onClick={() => setTimeControl(opt.value)}
                                      className={`px-2 py-1 text-[11px] font-medium rounded transition-all ${
                                        timeControl === opt.value
                                          ? "bg-gray-700 text-white"
                                          : "text-gray-500 hover:text-gray-300"
                                      }`}
                                    >
                                      {opt.label}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            </div>

                            {/* CTA */}
                            <button
                              disabled={!starts}
                              onClick={startAIGame}
                              className="w-full py-2 bg-green-600 hover:bg-green-500 disabled:opacity-30 disabled:cursor-not-allowed text-white text-sm font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                            >
                              <Swords className="w-3.5 h-3.5" />
                              Fight!
                            </button>
                          </motion.div>
                        </AnimatePresence>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            )}
          </div>
        )}

        {/* ── Online ── */}
        {tab === "online" && (
          <div className="max-w-md mx-auto space-y-4">
            {/* Time control with queue counts */}
            <div className="space-y-2">
              <span className="text-[11px] text-gray-500 uppercase tracking-wider">Time control</span>
              <div className="flex bg-gray-800 rounded-md p-0.5">
                {TIME_OPTIONS.map((opt) => (
                  <button
                    key={opt.label}
                    onClick={() => setTimeControl(opt.value)}
                    className={`flex-1 px-2 py-1 text-[11px] font-medium rounded transition-all ${
                      timeControl === opt.value
                        ? "bg-gray-700 text-white"
                        : "text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
              {(() => {
                const key = timeControl === null ? "null" : String(timeControl);
                const count = queueCounts[key] || 0;
                return (
                  <p className="text-[11px] text-gray-500 text-center">
                    {count > 0 ? `${count} player${count > 1 ? "s" : ""} searching` : "No players searching"}
                  </p>
                );
              })()}
            </div>

            {/* Quick Match */}
            <div className="p-4 rounded-xl border border-gray-700/50 bg-gray-800/40 space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-200">Quick Match</p>
                <p className="text-[11px] text-gray-500 mt-0.5">Find a random opponent instantly</p>
              </div>
              <button onClick={quickMatch} className="w-full py-2.5 bg-green-600 hover:bg-green-500 text-white text-sm font-bold rounded-lg transition-colors flex items-center justify-center gap-2">
                <Globe className="w-3.5 h-3.5" />
                Find Opponent
              </button>
            </div>

            {/* Private Lobby */}
            <div className="p-4 rounded-xl border border-gray-700/50 bg-gray-800/40 space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-200">Private Lobby</p>
                <p className="text-[11px] text-gray-500 mt-0.5">Play with a friend using a lobby code</p>
              </div>
              <button onClick={createLobby} className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs font-medium transition-colors">
                Create Lobby
              </button>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={lobbyInput}
                  onChange={(e) => setLobbyInput(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === "Enter" && joinLobby()}
                  placeholder="Enter code"
                  maxLength={4}
                  className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-xs font-mono tracking-widest text-center focus:outline-none focus:border-gray-500 transition-colors"
                />
                <button onClick={joinLobby} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs font-medium transition-colors">
                  Join
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Local ── */}
        {tab === "local" && (
          <div className="max-w-md mx-auto p-4 rounded-xl border border-gray-700/50 bg-gray-800/40 space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-200">Local Game</p>
              <p className="text-[11px] text-gray-500 mt-0.5">Pass and play on the same device</p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-gray-500 uppercase tracking-wider">First move</span>
                <div className="flex bg-gray-800 rounded-md p-0.5">
                  {(["player", "playerO"] as const).map((v) => (
                    <button
                      key={v}
                      onClick={() => setStarts(v)}
                      className={`px-3 py-1 text-[11px] font-medium rounded transition-all ${
                        starts === v
                          ? "bg-gray-700 text-white"
                          : "text-gray-500 hover:text-gray-300"
                      }`}
                    >
                      {v === "player" ? "Player X" : "Player O"}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[11px] text-gray-500 uppercase tracking-wider">Time</span>
                <div className="flex bg-gray-800 rounded-md p-0.5">
                  {TIME_OPTIONS.map((opt) => (
                    <button
                      key={opt.label}
                      onClick={() => setTimeControl(opt.value)}
                      className={`px-2 py-1 text-[11px] font-medium rounded transition-all ${
                        timeControl === opt.value
                          ? "bg-gray-700 text-white"
                          : "text-gray-500 hover:text-gray-300"
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={() => startLocalGame(starts || "player")}
              className="w-full py-2.5 bg-green-600 hover:bg-green-500 text-white text-sm font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Users className="w-3.5 h-3.5" />
              Start Game
            </button>
          </div>
        )}
      </div>

    </div>
  );
}
