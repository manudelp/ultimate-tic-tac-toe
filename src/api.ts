// src/api.ts
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

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

interface LoginResponse {
  access_token: string;
  name: string;
}

// Enhanced User interfaces
interface User {
  id: number;
  name: string;
  email: string;
}

interface RegisterResponse {
  message: string;
}

interface VerifyTokenResponse {
  valid: boolean;
  data?: {
    id: number;
    name: string;
    email: string;
    exp: number;
  };
}

// Connection
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
  try {
    const response = await axios.get<BotListResponse[]>(
      `${API_URL}/get-bot-list`
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
    await axios.post(`${API_URL}/agent-load`, { id });
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
      `${API_URL}/get-bot-move`,
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
    await axios.post(`${API_URL}/agents-reset`, { id });
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Failed to reset agents");
    }
    console.error("Error resetting agents:", error);
    throw new Error("Failed to reset agents. Please try again later.");
  }
};

// Register user
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
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Registration failed");
    }
    throw new Error("Registration failed");
  }
};

// Get current user from localStorage
export const getCurrentUser = (): User | null => {
  const userData = localStorage.getItem("userData");
  if (!userData) return null;

  try {
    return JSON.parse(userData) as User;
  } catch (error) {
    console.error("Error parsing user data:", error);
    return null;
  }
};

// Login user
export const loginUser = async (
  email: string,
  password: string
): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(`${API_URL}/login`, {
      email,
      password,
    });
    const { access_token, name } = response.data;

    // Save token in localStorage
    localStorage.setItem("token", access_token);

    // Store user data
    const userData = {
      name,
      email,
      // The id will be populated when verifying the token
    };
    localStorage.setItem("userData", JSON.stringify(userData));

    return { access_token, name };
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Login failed");
    }
    throw new Error("Login failed");
  }
};

// Logout user
export const logoutUser = (): void => {
  localStorage.removeItem("token");
  localStorage.removeItem("userData");
};

// Verify token
export const verifyToken = async (): Promise<VerifyTokenResponse> => {
  try {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No token found");

    const response = await axios.post<VerifyTokenResponse>(
      `${API_URL}/verify-token`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    // Update user data if verification is successful
    if (response.data.valid && response.data.data) {
      localStorage.setItem("userData", JSON.stringify(response.data.data));
    }

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(
        error.response.data.message || "Token verification failed"
      );
    }
    throw new Error("Token verification failed");
  }
};
