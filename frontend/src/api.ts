import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

interface BotListResponse {
  id: number;
  name: string;
  icon: string;
  description: string;
  difficulty: number;
}

interface BotMoveResponse {
  move: [number, number, number, number];
}

export const checkConnection = async (): Promise<boolean> => {
  try {
    const response = await api.get("/health");
    return response.status === 200;
  } catch {
    return false;
  }
};

export const getBots = async (): Promise<BotListResponse[]> => {
  try {
    const response = await axios.get<BotListResponse[]>(`${API_BASE_URL}/get-bot-list`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Failed to retrieve bot list");
    }
    throw new Error("Failed to retrieve bot list. Please try again later.");
  }
};

export const loadBot = async (id: number): Promise<void> => {
  try {
    await axios.post(`${API_BASE_URL}/agent-load`, { id });
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Failed to load bot");
    }
    throw new Error("Failed to load bot. Please try again later.");
  }
};

export const getBotMove = async (
  bot: number,
  board: number[][][][],
  activeMiniBoard: number[] | null,
  turn: string
): Promise<[number, number, number, number]> => {
  try {
    const response = await axios.post<BotMoveResponse>(
      `${API_BASE_URL}/get-bot-move`,
      { bot, board, activeMiniBoard, turn }
    );
    return response.data.move;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Failed to get bot move");
    }
    throw new Error("Failed to get bot move. Please try again later.");
  }
};

export const agentsReset = async (id: number): Promise<void> => {
  try {
    await axios.post(`${API_BASE_URL}/agents-reset`, { id });
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Failed to reset agents");
    }
    throw new Error("Failed to reset agents. Please try again later.");
  }
};

export default api;
