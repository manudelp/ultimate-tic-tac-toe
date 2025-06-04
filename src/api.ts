// src/api.ts
import axios from "axios";
import { supabase } from "@/lib/supabase";

// Base API URL - make sure it's correct
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

// Configure axios defaults
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to include the token in requests
api.interceptors.request.use(
  async (config) => {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Types
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

// Connection
export const checkConnection = async (): Promise<boolean> => {
  try {
    const response = await api.get("/health", {
      headers: {
        Authorization: undefined, // Exclude Authorization header if not required
      },
    });
    return response.status === 200;
  } catch (error) {
    console.error("Failed to connect to backend:", error);
    return false;
  }
};

// Bots
export const getBots = async (): Promise<BotListResponse[]> => {
  try {
    const response = await axios.get<BotListResponse[]>(
      `${API_BASE_URL}/get-bot-list`
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(
        error.response.data.message || "Failed to retrieve bot list"
      );
    }
    console.error("Error fetching bots:", error);
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
    console.error("Error loading bot:", error);
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
      {
        bot,
        board,
        activeMiniBoard,
        turn,
      }
    );
    return response.data.move;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Failed to get bot move");
    }
    console.error("Error getting bot move:", error);
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
    console.error("Error resetting agents:", error);
    throw new Error("Failed to reset agents. Please try again later.");
  }
};

// AUTH FUNCTIONS
export const registerUser = async (
  email: string,
  password: string,
  username: string
) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });
  if (error) throw new Error(error.message);

  const userId = data.user?.id;
  if (!userId) throw new Error("User ID missing");

  const { error: profileError, data: profileData } = await supabase
    .from("profiles")
    .insert({
      id: userId,
      email,
      username,
    })
    .select();

  if (profileError) {
    console.error("Profile insertion error:", profileError);
    throw new Error(profileError.message);
  }

  return { success: true, profileData };
};

export const loginUser = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  if (error) throw new Error(error.message);

  const token = data.session?.access_token;
  if (token) localStorage.setItem("token", token);
  return data.user;
};

export const logoutUser = async () => {
  const { error } = await supabase.auth.signOut();
  if (error) throw new Error(error.message);
  localStorage.removeItem("token");
  return { success: true };
};

// Verify token validity
export const verifyToken = async (): Promise<boolean> => {
  const { data } = await supabase.auth.getSession();
  return !!data.session;
};

export default api;
