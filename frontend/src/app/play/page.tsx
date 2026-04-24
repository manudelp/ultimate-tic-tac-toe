"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getBots } from "@/api";
import { toast } from "sonner";
import { Bot, Globe, Users } from "lucide-react";
import Loader from "@/components/ui/loader";
import type { BotInfo } from "@/types/game";
import Link from "next/link";

type Tab = "ai" | "online" | "local";

const TABS: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: "ai", label: "vs AI", icon: Bot },
  { id: "online", label: "Online", icon: Globe },
  { id: "local", label: "Local", icon: Users },
];

export default function Play() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("ai");

  // AI state
  const [bots, setBots] = useState<BotInfo[] | null>(null);
  const [selectedBot, setSelectedBot] = useState<BotInfo | null>(null);
  const [starts, setStarts] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Online state
  const [lobbyInput, setLobbyInput] = useState("");

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
      mode: "player-vs-bot", botId: selectedBot.id, bot: selectedBot, starts,
    }));
    router.push("/game");
  };

  const startLocalGame = (who: string) => {
    sessionStorage.setItem("uttt_game_config", JSON.stringify({
      mode: "player-vs-player", starts: who,
    }));
    router.push("/game");
  };

  const joinLobby = () => {
    const code = lobbyInput.trim().toUpperCase();
    if (code.length === 5) {
      sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", lobbyCode: code }));
      router.push("/game");
    } else {
      toast.error("Enter a valid 5-character lobby code.");
    }
  };

  const createLobby = () => {
    sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online" }));
    router.push("/game");
  };

  const quickMatch = () => {
    sessionStorage.setItem("uttt_game_config", JSON.stringify({ mode: "online", matchmaking: true }));
    router.push("/game");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-svh px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Play</h1>

      {/* Tabs */}
      <div className="flex bg-gray-800 rounded-lg p-1 mb-8">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => { setTab(id); setSelectedBot(null); setStarts(null); }}
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
      <div className="w-full max-w-md">
        {/* ── vs AI ── */}
        {tab === "ai" && (
          <div className="space-y-4">
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
              <>
                <div className="grid grid-cols-2 gap-3">
                  {bots?.sort((a, b) => a.difficulty - b.difficulty).map((bot) => (
                    <button
                      key={bot.id}
                      onClick={() => { setSelectedBot(selectedBot?.id === bot.id ? null : bot); setStarts(null); }}
                      className={`relative flex flex-col items-center gap-2 p-4 rounded-lg border transition-all ${
                        selectedBot?.id === bot.id
                          ? "border-blue-500 bg-gray-800"
                          : "border-gray-700 bg-gray-800/50 hover:border-gray-600"
                      }`}
                    >
                      <span className="text-3xl">{bot.icon}</span>
                      <span className="text-sm font-medium">{bot.name}</span>
                      <div className="flex gap-0.5">
                        {Array(5).fill(0).map((_, i) => (
                          <span key={i} className={`text-xs ${i < bot.difficulty ? "" : "opacity-30"}`}>
                            🔥
                          </span>
                        ))}
                      </div>
                    </button>
                  ))}
                </div>

                {selectedBot && (
                  <div className="p-4 bg-gray-800 rounded-lg border border-gray-700 space-y-4">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">{selectedBot.icon}</span>
                      <div>
                        <p className="font-semibold">{selectedBot.name}</p>
                        <p className="text-sm text-gray-400">{selectedBot.description}</p>
                      </div>
                    </div>

                    <div>
                      <p className="text-sm text-gray-400 mb-2">Who goes first?</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setStarts("player")}
                          className={`flex-1 py-2 text-sm rounded-md transition-colors ${
                            starts === "player" ? "bg-blue-600 text-white" : "bg-gray-700 hover:bg-gray-600"
                          }`}
                        >
                          You
                        </button>
                        <button
                          onClick={() => setStarts("bot")}
                          className={`flex-1 py-2 text-sm rounded-md transition-colors ${
                            starts === "bot" ? "bg-red-600 text-white" : "bg-gray-700 hover:bg-gray-600"
                          }`}
                        >
                          {selectedBot.name}
                        </button>
                      </div>
                    </div>

                    <button
                      disabled={!starts}
                      onClick={startAIGame}
                      className="w-full py-2.5 bg-green-600 hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
                    >
                      Start Game
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ── Online ── */}
        {tab === "online" && (
          <div className="space-y-4">
            <div className="p-5 bg-gray-800 rounded-lg border border-gray-700 space-y-3">
              <p className="font-medium">Private Lobby</p>
              <button onClick={createLobby} className="w-full py-2.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors">
                Create Lobby
              </button>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={lobbyInput}
                  onChange={(e) => setLobbyInput(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === "Enter" && joinLobby()}
                  placeholder="Lobby code"
                  maxLength={5}
                  className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button onClick={joinLobby} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors">
                  Join
                </button>
              </div>
            </div>

            <div className="p-5 bg-gray-800 rounded-lg border border-gray-700 space-y-3">
              <p className="font-medium">Quick Match</p>
              <p className="text-sm text-gray-400">Find a random opponent</p>
              <button onClick={quickMatch} className="w-full py-2.5 bg-green-600 hover:bg-green-500 text-white font-semibold rounded-lg transition-colors">
                Find Opponent
              </button>
            </div>
          </div>
        )}

        {/* ── Local ── */}
        {tab === "local" && (
          <div className="p-5 bg-gray-800 rounded-lg border border-gray-700 space-y-4">
            <p className="text-center text-gray-400">Pass and play on the same device</p>
            <p className="text-sm text-gray-400 text-center">Who goes first?</p>
            <div className="flex gap-3">
              <button
                onClick={() => startLocalGame("player")}
                className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors"
              >
                Player X
              </button>
              <button
                onClick={() => startLocalGame("bot")}
                className="flex-1 py-3 bg-red-600 hover:bg-red-500 text-white font-medium rounded-lg transition-colors"
              >
                Player O
              </button>
            </div>
          </div>
        )}
      </div>

      <Link href="/" className="mt-8 text-sm text-gray-500 hover:text-gray-300 transition-colors">
        Back to home
      </Link>
    </div>
  );
}
