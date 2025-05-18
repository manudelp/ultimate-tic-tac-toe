// src/socket.ts
import { io, Socket } from "socket.io-client";
import { DefaultEventsMap } from "@socket.io/component-emitter";

// Set the API URL for socket connection
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Store the socket instance
let socket: Socket<DefaultEventsMap, DefaultEventsMap> | null = null;

// Function to get or create a socket connection
export const getSocket = (): Socket<DefaultEventsMap, DefaultEventsMap> => {
  if (!socket) {
    socket = io(API_URL, {
      transports: ["websocket", "polling"], // Try WebSocket first, fallback to polling
      reconnection: true, // Enable reconnection
      reconnectionAttempts: 5, // Set max reconnection attempts
      reconnectionDelay: 1000, // Start with a 1s delay
      reconnectionDelayMax: 5000, // Max delay of 5s
      timeout: 20000, // Connection timeout
    });

    // Add connection event handlers for debugging
    socket.on("connect", () => {
      console.log("Socket connected!", socket?.id);
    });

    socket.on("connect_error", (error) => {
      console.error("Socket connection error:", error);
    });

    socket.on("disconnect", (reason) => {
      console.log("Socket disconnected:", reason);
    });

    socket.on("reconnect_attempt", (attemptNumber) => {
      console.log(`Socket reconnection attempt ${attemptNumber}`);
    });
  }

  return socket;
};

// Function to disconnect the socket
export const disconnectSocket = (): void => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

// For backward compatibility
const socketUtils = { getSocket, disconnectSocket };
export default socketUtils;
