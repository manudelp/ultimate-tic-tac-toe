import { io, Socket } from "socket.io-client";
import { DefaultEventsMap } from "@socket.io/component-emitter";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

let socket: Socket<DefaultEventsMap, DefaultEventsMap> | null = null;

export const getSocket = (): Socket<DefaultEventsMap, DefaultEventsMap> => {
  if (!socket) {
    socket = io(API_URL + "/online", {
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
      forceNew: true,
    });

    socket.on("connect_error", (error) => {
      console.error("Socket connection error:", error);
    });
  }

  return socket;
};

export const disconnectSocket = (): void => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

export const reconnectSocket = (): void => {
  disconnectSocket();
  getSocket();
};

const socketUtils = { getSocket, disconnectSocket, reconnectSocket };
export default socketUtils;
