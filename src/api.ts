// src/api.ts
import axios from "axios";

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
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
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
    const response = await axios.get(`${API_BASE_URL}/health`);
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
  username: string,
  email: string,
  password: string,
  recaptcha: string
) => {
  try {
    console.log("Registering user:", {
      username,
      email,
      recaptchaLength: recaptcha?.length || 0,
    });

    // Validate recaptcha token
    if (!recaptcha || recaptcha.length < 10) {
      throw new Error("Invalid reCAPTCHA token");
    }

    const response = await api.post("/register", {
      name: username,
      email,
      password,
      recaptcha,
    });
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.error(
        "Registration error:",
        error.response?.data || error.message
      );
      throw new Error(error.response?.data?.message || "Registration failed");
    }
    console.error("Registration error:", error);
    throw new Error(
      error instanceof Error ? error.message : "Registration failed"
    );
  }
};

export const loginUser = async (
  email: string,
  password: string,
  recaptcha: string
) => {
  try {
    console.log("Logging in user:", {
      email,
      recaptchaLength: recaptcha?.length || 0,
    });

    // Validate recaptcha token
    if (!recaptcha || recaptcha.length < 10) {
      throw new Error("Invalid reCAPTCHA token");
    }

    const response = await api.post("/login", {
      email,
      password,
      recaptcha,
    });

    // Store the token
    if (response.data.access_token) {
      localStorage.setItem("token", response.data.access_token);
    }

    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.error("Login error:", error.response?.data || error.message);
      throw new Error(error.response?.data?.message || "Login failed");
    }
    console.error("Login error:", error);
    throw new Error("Login failed");
  }
};

export const logoutUser = () => {
  try {
    localStorage.removeItem("token");
    localStorage.removeItem("userData");
    return { success: true };
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.error("Logout error:", error.response?.data || error.message);
      throw new Error(error.response?.data?.message || "Logout failed");
    }
    console.error("Logout error:", error);
    throw new Error("Logout failed");
  }
};

// Verify token validity
export const verifyToken = async (): Promise<boolean> => {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      return false;
    }

    const response = await api.post(
      "/verify-token",
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.status === 200;
  } catch (error) {
    console.error("Token verification failed:", error);
    return false;
  }
};

export default api;
