// src/socket.ts
import { io, Socket } from "socket.io-client";

const SOCKET_URL =
  process.env.NEXT_PUBLIC_SOCKET_URL || "http://127.0.0.1:5000";

// Store the socket instance
let socket: Socket | null = null;

// Function to get or create a socket connection
export const getSocket = (): Socket => {
  if (!socket) {
    socket = io(`${SOCKET_URL}/online`);
    console.log("Socket connected to online namespace");
  }
  return socket;
};

// Function to disconnect the socket
export const disconnectSocket = (): void => {
  if (socket) {
    socket.disconnect();
    socket = null;
    console.log("Socket disconnected");
  }
};

// For backward compatibility
const socketUtils = { getSocket, disconnectSocket };
export default socketUtils;
