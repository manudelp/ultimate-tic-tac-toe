"use client";
import React from "react";
import { useEffect, useState } from "react";
import { getBots, loadBot } from "@/api";
import Board from "@/components/core/board";
import Button from "@/components/ui/button-2";
import Loader from "@/components/ui/loader";
import Share from "@/components/ui/share";
import { motion, AnimatePresence } from "framer-motion";
// import { toast } from "sonner";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from "@/components/ui/tooltip";

// Types
type BotListResponse = {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: number;
};

export default function Bot() {
  // State variables
  const [starts, setStarts] = useState<string | null>(null);
  const [bots, setBots] = useState<BotListResponse[] | null>(null);
  const [selectedBot, setSelectedBot] = useState<BotListResponse | null>(null);
  const [bot, setBot] = useState<BotListResponse | null>(null);
  const [botsLoaded, setBotsLoaded] = useState<boolean[]>([]);
  const [loading, setLoading] = useState(true);
  const [width, setWidth] = useState(0);

  const handleExitGame = () => {
    setBots(null);
    setSelectedBot(null);
    setBot(null);
    setStarts(null);
  };

  const updateBotsLoaded = (id: number) => {
    setBotsLoaded((prev) => {
      const updated = [...prev];
      updated[id] = true;
      return updated;
    });
  };

  useEffect(() => {
    if (!bots) {
      setLoading(true);
      getBots().then((bots) => {
        setBots(bots.map((bot: BotListResponse) => ({ ...bot })));
        setLoading(false);

        bots.forEach((bot) => {
          loadBot(bot.id).then(() => {
            updateBotsLoaded(bot.id);
          });
        });
      });
    }
  }, [bots]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setWidth(window.innerWidth);
      const handleResize = () => setWidth(window.innerWidth);
      window.addEventListener("resize", handleResize);
      return () => window.removeEventListener("resize", handleResize);
    }
  }, []);

  return (
    <div className="flex flex-col items-center justify-center px-4 py-8 min-h-svh sm:px-8 sm:py-16">
      {/* Game container */}
      {bot && starts ? (
        <Board
          gameMode="player-vs-bot"
          bot={bot}
          starts={starts}
          onExit={handleExitGame}
        />
      ) : (
        <div className="w-full max-w-3xl pt-4 mx-auto">
          <h1 className="mb-8 text-3xl font-bold sm:text-4xl text-center bg-gradient-to-r from-pink-400 to-yellow-500 text-transparent bg-clip-text">
            Ready to play?
          </h1>

          <h2 className="mb-6 text-xl font-semibold text-center sm:text-2xl">
            Select your opponent
          </h2>

          {loading ? (
            <div className="flex flex-col items-center justify-center h-48 bg-gray-800 border border-gray-700 rounded-lg">
              <Loader />
              <p className="mt-4 text-sm text-gray-400">Loading opponents...</p>
            </div>
          ) : (
            <div className="flex flex-col h-full gap-4 md:flex-row">
              {/* Bot selection grid */}
              <div className="w-full md:w-1/2">
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-2 md:grid-cols-2">
                  {bots
                    ?.sort((a, b) => a.difficulty - b.difficulty)
                    .map((botOption, index) => (
                      <motion.div
                        key={botOption.id}
                        initial={{ opacity: 0 }}
                        animate={{
                          opacity: botsLoaded[botOption.id] ? 1 : 0.6,
                        }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                        className={`cursor-pointer relative bg-gray-800 rounded-lg h-48 flex flex-col justify-center
                        overflow-hidden border hover:border-blue-500/50 ${
                          selectedBot?.id === botOption.id
                            ? "border-blue-500"
                            : "border-gray-700"
                        }`}
                        onClick={() => {
                          if (botsLoaded[botOption.id]) {
                            setSelectedBot(
                              selectedBot?.id === botOption.id
                                ? null
                                : botOption
                            );
                            setStarts(null);
                          }
                        }}
                      >
                        <div className="flex flex-col items-center p-3">
                          {/* Bot avatar - simplified */}
                          <div
                            className={`relative rounded-full text-4xl w-16 h-16 flex items-center justify-center mb-2 ${
                              botOption.id === -1 ? "bg-black" : "bg-gray-700"
                            }`}
                            style={
                              botOption.id === -1
                                ? { backgroundImage: `url('/fire.gif')` }
                                : undefined
                            }
                          >
                            {botOption.icon}
                            {selectedBot?.id === botOption.id && (
                              <div className="absolute inset-0 border border-blue-400 rounded-full"></div>
                            )}
                          </div>

                          {/* Bot info - streamlined */}
                          <h3 className="text-base font-medium text-center">
                            {botOption.name}
                          </h3>

                          {/* Difficulty rating - more compact */}
                          <TooltipProvider delayDuration={0}>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div className="flex justify-center mt-1">
                                  {Array(5)
                                    .fill(0)
                                    .map((_, i) => (
                                      <span key={i} className="text-sm mx-0.5">
                                        {i < botOption.difficulty ? (
                                          "🔥"
                                        ) : (
                                          <span className="bg-gray-500 bg-clip-text text-transparent">
                                            🔥
                                          </span>
                                        )}
                                      </span>
                                    ))}
                                </div>
                              </TooltipTrigger>
                              <TooltipContent
                                side="bottom"
                                className="!bg-gray-700 !text-gray-200"
                              >
                                <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-700 rotate-45 z-[-1]" />

                                <p className="text-xs">
                                  Difficulty: {botOption.difficulty} / 5 (
                                  {botOption.difficulty < 3
                                    ? "Easy"
                                    : botOption.difficulty < 5
                                    ? "Medium"
                                    : "Hard"}
                                  )
                                </p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        </div>

                        {/* Loading indicator */}
                        {!botsLoaded[botOption.id] && (
                          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-60">
                            <Loader />
                          </div>
                        )}
                      </motion.div>
                    ))}
                </div>
              </div>

              {/* Bot details panel */}
              <div className="w-full md:w-1/2">
                <AnimatePresence mode="wait">
                  {selectedBot ? (
                    <motion.div
                      key="bot-details"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="flex flex-col justify-between h-full p-4 space-y-6 bg-gray-800 border border-gray-700 rounded-lg sm:space-y-0"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center text-4xl bg-gray-700 rounded-full w-14 h-14">
                          {selectedBot.icon}
                        </div>
                        <div>
                          <h2 className="text-xl font-bold">
                            {selectedBot.name}
                          </h2>

                          <div className="flex mt-1">
                            {Array(selectedBot.difficulty)
                              .fill("🔥")
                              .map((fire, i) => (
                                <span key={i} className="text-base">
                                  {fire}
                                </span>
                              ))}
                            {Array(5 - selectedBot.difficulty)
                              .fill("🔥")
                              .map((fire, i) => (
                                <span
                                  key={i}
                                  className="text-base bg-gray-500 bg-clip-text text-transparent"
                                >
                                  {fire}
                                </span>
                              ))}
                          </div>
                        </div>
                      </div>

                      {/* <p className="h-10 pr-2 overflow-y-auto text-sm text-gray-300 scrollbar-thin scrollbar-thumb-gray-600"> */}
                      <p className="text-gray-300">{selectedBot.description}</p>

                      <div className="flex flex-col gap-3">
                        {/* Who starts section - simplified */}
                        <div>
                          <h3 className="mb-2 text-sm font-medium text-center">
                            First move
                          </h3>
                          <div className="flex gap-2">
                            <button
                              className={`flex-1 py-2 text-xs font-medium rounded-md transition-all ${
                                starts === "player"
                                  ? "bg-blue-600 text-white"
                                  : "bg-gray-700 hover:bg-gray-600"
                              }`}
                              onClick={() => setStarts("player")}
                            >
                              You Start
                            </button>
                            <button
                              className={`flex-1 py-2 text-xs font-medium rounded-md transition-all ${
                                starts === "bot"
                                  ? "bg-red-600 text-white"
                                  : "bg-gray-700 hover:bg-gray-600"
                              }`}
                              onClick={() => setStarts("bot")}
                            >
                              {selectedBot.name} Starts
                            </button>
                          </div>
                        </div>

                        <Button
                          text="Start Game"
                          variant="success"
                          className={`!w-full !py-2 text-sm ${
                            !starts ? "opacity-50 cursor-not-allowed" : ""
                          }`}
                          disabled={!starts}
                          onClick={() => setBot(selectedBot)}
                        />
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="select-prompt"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="flex flex-col items-center justify-center h-full p-4 space-y-3 bg-gray-800 border border-gray-700 rounded-lg"
                    >
                      <div className="mb-3 text-4xl">
                        {width > 768 ? "👈" : "👆"}
                      </div>
                      <h3 className="text-lg font-medium text-center text-gray-300">
                        Select an opponent
                      </h3>
                      <p className="mt-1 text-base text-center text-gray-400">
                        Choose from the available bots
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          )}
          <div className="flex justify-center mt-3">
            <Button
              text="Back to Menu"
              variant="danger"
              onClick={() => (window.location.href = "/")}
            />
          </div>
        </div>
      )}

      <Share />
    </div>
  );
}
