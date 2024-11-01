import axios from "axios";

// src/api.ts

const API_URL = "http://127.0.0.1:5000";

// Types
interface BotNamesResponse {
  agent1_name: string;
  agent2_name: string;
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

// Bots
export const fetchBotNames = async (): Promise<BotNamesResponse> => {
  try {
    const response = await axios.get<{
      agent1_name: string;
      agent2_name: string;
    }>(`${API_URL}/get-bot-names`);
    return {
      agent1_name: response.data.agent1_name,
      agent2_name: response.data.agent2_name,
    };
  } catch (error) {
    console.error("Error fetching bot names:", error);
    throw error;
  }
};

export const getBotMove = async (
  board: number[][][][],
  activeMiniBoard: number[] | null,
  turn: string
): Promise<[number, number, number, number]> => {
  const response = await axios.post<BotMoveResponse>(
    `${API_URL}/get-bot-move`,
    {
      board,
      activeMiniBoard,
      turn,
    }
  );
  return response.data.move;
};

export const agentsReset = async (): Promise<void> => {
  await axios.post(`${API_URL}/agents-reset`);
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
