import { createClient } from "@supabase/supabase-js";

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
  return createClient(supabaseUrl, supabaseKey);
};

export const supabase = createSupabaseClient();
