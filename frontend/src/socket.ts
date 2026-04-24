import { io, Socket } from "socket.io-client";
import { DefaultEventsMap } from "@socket.io/component-emitter";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

let socket: Socket<DefaultEventsMap, DefaultEventsMap> | null = null;

export function getSocket(): Socket<DefaultEventsMap, DefaultEventsMap> {
  if (!socket || socket.disconnected) {
    socket = io(API_URL + "/game", {
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 20000,
    });
  }
  return socket;
}

export function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}
