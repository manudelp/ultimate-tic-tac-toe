// src/socket.ts
import { io } from "socket.io-client";

const SOCKET_URL =
  process.env.NEXT_PUBLIC_SOCKET_URL || "http://127.0.0.1:5000";

const socket = io(`${SOCKET_URL}/online`);

export default socket;
