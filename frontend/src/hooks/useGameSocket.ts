import { useState, useEffect, useCallback, useRef } from "react";
import { getSocket, disconnectSocket } from "@/socket";
import type { Socket } from "socket.io-client";
import type { DefaultEventsMap } from "@socket.io/component-emitter";
import type { GameState, GameStartedEvent } from "@/types/game";

interface FindGameParams {
  mode: "bot" | "local" | "matchmaking" | "lobby_create" | "lobby_join";
  botId?: number;
  starts?: string;
  gameId?: string;
  timeControl?: number | null;
}

export function useGameSocket() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [myPlayer, setMyPlayer] = useState<"X" | "O" | null>(null);
  const [gameId, setGameId] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [searching, setSearching] = useState(false);
  const [lobbyId, setLobbyId] = useState<string | null>(null);
  const [opponent, setOpponent] = useState<{ type: "bot"; name: string; icon: string } | null>(null);
  const [isLocal, setIsLocal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<Socket<DefaultEventsMap, DefaultEventsMap> | null>(null);

  useEffect(() => {
    const socket = getSocket();
    socketRef.current = socket;

    if (socket.connected) setConnected(true);

    const onConnect = () => setConnected(true);
    const onDisconnect = () => setConnected(false);
    const onGameStarted = (data: GameStartedEvent) => {
      setGameId(data.gameId);
      setMyPlayer(data.yourPlayer);
      setGameState(data.state);
      setSearching(false);
      setError(null);
      if (data.opponent) setOpponent(data.opponent);
      if (data.local) setIsLocal(true);
      sessionStorage.setItem("uttt_resume", JSON.stringify({
        gameId: data.gameId,
        myPlayer: data.yourPlayer,
        opponent: data.opponent ?? null,
        isLocal: data.local ?? false,
      }));
    };
    const onGameState = (state: GameState) => setGameState(state);
    const onLobbyCreated = (data: { gameId: string }) => setLobbyId(data.gameId);
    const onSearching = () => setSearching(true);
    const onOpponentLeft = () => setError("Opponent disconnected — waiting for them to rejoin...");
    const onOpponentRejoined = () => setError(null);
    const onError = (data: { message: string }) => {
      setError(data.message);
      setSearching(false);
    };
    const onRejoinFailed = () => {
      sessionStorage.removeItem("uttt_resume");
      setError("Could not rejoin game — it may have expired");
    };

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("game_started", onGameStarted);
    socket.on("game_state", onGameState);
    socket.on("lobby_created", onLobbyCreated);
    socket.on("searching", onSearching);
    socket.on("opponent_left", onOpponentLeft);
    socket.on("opponent_rejoined", onOpponentRejoined);
    socket.on("error", onError);
    socket.on("rejoin_failed", onRejoinFailed);

    return () => {
      socket.off("connect", onConnect);
      socket.off("disconnect", onDisconnect);
      socket.off("game_started", onGameStarted);
      socket.off("game_state", onGameState);
      socket.off("lobby_created", onLobbyCreated);
      socket.off("searching", onSearching);
      socket.off("opponent_left", onOpponentLeft);
      socket.off("opponent_rejoined", onOpponentRejoined);
      socket.off("error", onError);
      socket.off("rejoin_failed", onRejoinFailed);
      // Do NOT disconnect here — only on explicit disconnect() call
    };
  }, []);

  const rejoinGame = useCallback((gameId: string, myPlayer: "X" | "O", opponent: { type: "bot"; name: string; icon: string } | null, isLocal: boolean) => {
    setError(null);
    setMyPlayer(myPlayer);
    setGameId(gameId);
    if (opponent) setOpponent(opponent);
    if (isLocal) setIsLocal(true);
    socketRef.current?.emit("rejoin_game", { gameId, myPlayer });
  }, []);

  const findGame = useCallback((params: FindGameParams) => {
    setError(null);
    setIsLocal(false);
    setGameState(null);
    setGameId(null);
    setMyPlayer(null);
    setLobbyId(null);
    setOpponent(null);
    socketRef.current?.emit("find_game", params);
  }, []);

  const makeMove = useCallback((a: number, b: number, c: number, d: number) => {
    socketRef.current?.emit("make_move", { a, b, c, d });
  }, []);

  const resign = useCallback(() => {
    socketRef.current?.emit("resign", {});
  }, []);

  const disconnect = useCallback(() => {
    sessionStorage.removeItem("uttt_resume");
    disconnectSocket();
    socketRef.current = null;
  }, []);

  return {
    gameState, myPlayer, gameId, connected, searching,
    lobbyId, opponent, isLocal, error,
    findGame, rejoinGame, makeMove, resign, disconnect,
  };
}
