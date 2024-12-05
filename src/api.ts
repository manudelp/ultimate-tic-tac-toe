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

interface LoginResponse {
  access_token: string;
  name: string;
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

export const agentsReset = async (id: number): Promise<void> => {
  await axios.post(`${API_URL}/agents-reset`, {
    id,
  });
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

// Example protected route call
export const fetchProtectedData = async (
  endpoint: string
): Promise<unknown> => {
  try {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No token found");

    const response = await axios.get(`${API_URL}/${endpoint}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || "Request failed");
    }
    throw new Error("Request failed");
  }
};
