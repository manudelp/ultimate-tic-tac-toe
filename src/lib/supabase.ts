import { createClient } from "@supabase/supabase-js";
import { User } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY || "";

// Only throw error in browser environment or when actually using the client
const createSupabaseClient = () => {
  if (!supabaseUrl || !supabaseKey) {
    if (typeof window !== "undefined") {
      throw new Error("Missing Supabase environment variables");
    }
    // Return a mock client for build-time
    return {} as ReturnType<typeof createClient>;
  }
  return createClient(supabaseUrl, supabaseKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });
};

export const supabase = createSupabaseClient();

// Helper to get normalized user data
export const getNormalizedUserData = (user: User) => {
  if (!user) return null;

  // Extract data based on provider
  const isGoogleUser = user.app_metadata?.provider === "google";

  return {
    id: user.id,
    email: user.email,
    name: isGoogleUser
      ? user.user_metadata?.full_name || user.user_metadata?.name
      : user.user_metadata?.name || user.email?.split("@")[0],
    username: isGoogleUser
      ? user.user_metadata?.user_name || user.email?.split("@")[0]
      : user.user_metadata?.username || user.email?.split("@")[0],
    avatar_url: isGoogleUser
      ? user.user_metadata?.avatar_url
      : user.user_metadata?.avatar_url || "",
    provider: user.app_metadata?.provider || "email",
    emailVerified: user.email_confirmed_at ? true : false,
  };
};

// Helper to check if session is valid
export const validateSession = async () => {
  try {
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();
    if (error) {
      console.error("Session validation error:", error);
      return null;
    }
    return session;
  } catch (error) {
    console.error("Session validation failed:", error);
    return null;
  }
};
