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
  async (config) => {
    // Use backend token instead of Supabase token
    const token = localStorage.getItem("token");
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

// User data interface for Supabase token exchange
interface SupabaseUserData {
  id: string;
  email?: string;
  username?: string;
  name?: string;
  avatar_url?: string;
  provider?: string;
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
    console.error("API connection failed:", error);
    return false;
  }
};

// Bots - Update to use backend token
export const getBots = async (): Promise<BotListResponse[]> => {
  try {
    const token = localStorage.getItem("token");
    const response = await axios.get<BotListResponse[]>(
      `${API_BASE_URL}/get-bot-list`,
      {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(
        error.response.data.message || "Failed to retrieve bot list"
      );
    }
    throw new Error("Failed to retrieve bot list. Please try again later.");
  }
};

export const loadBot = async (id: number): Promise<void> => {
  try {
    const token = localStorage.getItem("token");
    await axios.post(
      `${API_BASE_URL}/agent-load`,
      { id },
      {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );
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
    const token = localStorage.getItem("token");
    const response = await axios.post<BotMoveResponse>(
      `${API_BASE_URL}/get-bot-move`,
      {
        bot,
        board,
        activeMiniBoard,
        turn,
      },
      {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
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
    const token = localStorage.getItem("token");
    await axios.post(
      `${API_BASE_URL}/agents-reset`,
      { id },
      {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Failed to reset agents");
    }
    throw new Error("Failed to reset agents. Please try again later.");
  }
};

// Test reCAPTCHA validation
export const testRecaptcha = async (token: string): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/test-recaptcha`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recaptcha: token }),
    });

    const data = await response.json();

    return response.ok && data.valid === true;
  } catch (error) {
    console.error("reCAPTCHA validation failed:", error);
    return false;
  }
};

// AUTH FUNCTIONS
export async function loginUser(
  email: string,
  password: string,
  recaptcha: string
) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, recaptcha }),
    });

    if (!response.ok) {
      let errorData;
      const contentType = response.headers.get("content-type");

      // Check if response is JSON
      if (contentType && contentType.includes("application/json")) {
        errorData = await response.json();

        // Provide more specific error messages for reCAPTCHA issues
        if (
          errorData.message &&
          errorData.message.toLowerCase().includes("recaptcha")
        ) {
          throw new Error(
            "Security verification failed. Please refresh the page and try again."
          );
        }

        throw new Error(errorData.message || "Login failed");
      } else {
        // If not JSON, it's likely an HTML error page
        const textContent = await response.text();
        console.error("Non-JSON error response:", textContent);
        throw new Error(
          `Server error: ${response.status} - ${response.statusText}`
        );
      }
    }

    const data = await response.json();

    // Store token and user data - no provider-specific handling
    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("userData", JSON.stringify(data.user));
    }

    return data;
  } catch (error) {
    throw error;
  }
}

export const registerUser = async (
  email: string,
  password: string,
  username: string,
  recaptcha: string
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, username, recaptcha }),
    });

    if (!response.ok) {
      let errorData;
      const contentType = response.headers.get("content-type");

      // Check if response is JSON
      if (contentType && contentType.includes("application/json")) {
        errorData = await response.json();
        throw new Error(errorData.message || "Registration failed");
      } else {
        // If not JSON, it's likely an HTML error page
        const textContent = await response.text();
        console.error("Non-JSON error response:", textContent);
        throw new Error(
          `Server error: ${response.status} - ${response.statusText}`
        );
      }
    }

    const result = await response.json();
    return result;
  } catch (error) {
    throw error;
  }
};

export const verifyToken = async (): Promise<boolean> => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/verify-token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) return false;

    const data = await response.json();

    // Update stored user data if verification succeeds
    if (data.valid && data.user) {
      localStorage.setItem("userData", JSON.stringify(data.user));
    }

    return data.valid === true;
  } catch (error) {
    console.error("Token verification failed:", error);
    return false;
  }
};

// New function to exchange Supabase token for backend token
export const exchangeSupabaseToken = async (
  supabaseToken: string,
  userData: SupabaseUserData
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/supabase-exchange`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        supabase_token: supabaseToken,
        user_data: userData,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Token exchange failed");
    }

    const data = await response.json();

    // Store the backend token and user data
    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("userData", JSON.stringify(data.user));
    }

    return data;
  } catch (error) {
    throw error;
  }
};

export const logoutUser = async () => {
  localStorage.removeItem("token");
  localStorage.removeItem("userData");
  return { success: true };
};

export default api;
