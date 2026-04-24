import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export interface BotListItem {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: number;
}

export async function getBots(): Promise<BotListItem[]> {
  const response = await axios.get<BotListItem[]>(`${API_BASE_URL}/get-bot-list`);
  return response.data;
}
