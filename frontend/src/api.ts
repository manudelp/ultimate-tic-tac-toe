import axios from "axios";
import type { BotInfo } from "@/types/game";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export async function getBots(): Promise<BotInfo[]> {
  const response = await axios.get<BotInfo[]>(`${API_BASE_URL}/get-bot-list`);
  return response.data;
}
