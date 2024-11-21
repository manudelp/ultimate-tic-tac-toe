import axios from "axios";

// src/api.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

// Types
interface BotListResponse {
  id: number;
  name: string;
  icon: string;
}

interface BotMoveResponse {
  move: [number, number, number, number];
}

interface RegisterResponse {
  message: string;
}

interface LoginResponse {
  access_token: string;
  name: string;
}

// Conection
export const checkConnection = async (): Promise<boolean> => {
  try {
    const response = await axios.get(`${API_URL}/health`);
    return response.status === 200;
  } catch (error) {
    console.error("Failed to connect to backend:", error);
    return false;
  }
};

// Bots
export const getBots = async (): Promise<BotListResponse[]> => {
  const response = await axios.get<BotListResponse[]>(
    `${API_URL}/get-bot-list`
  );
  return response.data;
};

export const getBotMove = async (
  bot: number,
  board: number[][][][],
  activeMiniBoard: number[] | null,
  turn: string
): Promise<[number, number, number, number]> => {
  const response = await axios.post<BotMoveResponse>(
    `${API_URL}/get-bot-move`,
    {
      bot,
      board,
      activeMiniBoard,
      turn,
    }
  );
  return response.data.move;
};

export const agentsReset = async (bot: BotListResponse): Promise<void> => {
  await axios.post(`${API_URL}/agents-reset`, {
    bot1: bot,
  });
};

// User Registration
export const registerUser = async (
  name: string,
  email: string,
  password: string
): Promise<RegisterResponse> => {
  try {
    const response = await axios.post<RegisterResponse>(`${API_URL}/register`, {
      name,
      email,
      password,
    });
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Registration failed");
    } else {
      throw new Error("Registration failed");
    }
  }
};

// User Login
export const loginUser = async (
  email: string,
  password: string
): Promise<{ token: string; name: string }> => {
  try {
    const response = await axios.post<LoginResponse>(`${API_URL}/login`, {
      email,
      password,
    });
    const { access_token, name } = response.data;
    localStorage.setItem("token", access_token);
    return { token: access_token, name };
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Login failed");
    } else {
      throw new Error("Login failed");
    }
  }
};

// Function to fetch data with JWT token
export const fetchProtectedData = async (
  endpoint: string
): Promise<unknown> => {
  const token = localStorage.getItem("token");
  const response = await axios.get(`${API_URL}/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};
