import { createClient } from "@supabase/supabase-js";
import { User as SupabaseUser } from "@supabase/supabase-js";
import {
  TypedSupabaseUser,
  ProfileData,
  NormalizedUserData,
  UIUserData,
  AccountLinkingResult,
  LinkedAccount,
  SessionValidationResult,
  ProfileUpdateResult,
  ProfileUpdateData,
} from "@/types/auth";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY || "";

// Type-safe client creation
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

// Type guard for Supabase user
const isValidSupabaseUser = (
  user: SupabaseUser | null
): user is TypedSupabaseUser => {
  return (
    user !== null &&
    typeof user.id === "string" &&
    typeof user.email === "string"
  );
};

// Helper to get normalized user data with profile priority
export const getNormalizedUserData = (
  user: SupabaseUser,
  profileData?: ProfileData | null
): NormalizedUserData | null => {
  if (!isValidSupabaseUser(user)) {
    return null;
  }

  try {
    // Extract data based on provider for internal processing only
    const isGoogleUser = user.app_metadata?.provider === "google";

    // Default data from OAuth/auth with fallbacks
    const authData: NormalizedUserData = {
      id: user.id,
      email: user.email || "",
      name: isGoogleUser
        ? user.user_metadata?.full_name ||
          user.user_metadata?.name ||
          user.email?.split("@")[0] ||
          "User"
        : user.user_metadata?.name || user.email?.split("@")[0] || "User",
      username: isGoogleUser
        ? user.user_metadata?.user_name || user.email?.split("@")[0] || "user"
        : user.user_metadata?.username || user.email?.split("@")[0] || "user",
      avatar_url: isGoogleUser
        ? user.user_metadata?.avatar_url || ""
        : user.user_metadata?.avatar_url || "",
      provider: (user.app_metadata?.provider as "google" | "email") || "email",
      emailVerified: Boolean(user.email_confirmed_at),
    };

    // If profile data is provided, it takes priority
    if (profileData) {
      return {
        ...authData,
        name: profileData.name || authData.name,
        username: profileData.username || authData.username,
        avatar_url: profileData.avatar_url || authData.avatar_url,
        provider: profileData.provider || authData.provider,
        _originalAuthData: authData,
      };
    }

    return authData;
  } catch {
    return null;
  }
};

// New helper to convert normalized data to provider-agnostic UI data
export const toUIUserData = (userData: NormalizedUserData): UIUserData => {
  return {
    name: userData.name,
    username: userData.username,
    image: userData.avatar_url,
  };
};

// Function to find and link accounts with the same email
export const findAndLinkAccounts = async (
  userEmail: string,
  currentUserId: string
): Promise<ProfileData | null> => {
  if (!userEmail || typeof window === "undefined" || !supabase.from) {
    return null;
  }

  try {
    // Look for existing profiles with the same email but different user ID
    const { data: existingProfiles } = await supabase
      .from("profiles")
      .select("*")
      .eq("email", userEmail)
      .neq("id", currentUserId)
      .is("linked_to", null); // Only get profiles that aren't already linked

    if (existingProfiles && existingProfiles.length > 0) {
      // Found existing account(s) with same email
      const primaryProfile = existingProfiles[0] as ProfileData;
      return primaryProfile;
    }

    return null;
  } catch {
    return null;
  }
};

// Function to merge profile data when linking accounts
export const mergeProfileData = async (
  currentUserId: string,
  existingProfile: ProfileData,
  newUserData: NormalizedUserData
): Promise<AccountLinkingResult> => {
  if (typeof window === "undefined" || !supabase.from) {
    return { success: false, error: "Client-side only operation" };
  }

  try {
    // Parse existing linked accounts
    let existingLinkedAccounts: LinkedAccount[] = [];
    if (existingProfile.linked_accounts) {
      try {
        existingLinkedAccounts = JSON.parse(existingProfile.linked_accounts);
      } catch {
        // Silent handling of parse errors
      }
    }

    // Merge strategy: existing profile data takes priority, but fill in gaps
    const mergedData: Omit<ProfileData, "created_at" | "updated_at"> = {
      id: currentUserId, // Keep current user ID
      email: newUserData.email,
      username: existingProfile.username || newUserData.username,
      name: existingProfile.name || newUserData.name,
      avatar_url: existingProfile.avatar_url || newUserData.avatar_url,
      provider: newUserData.provider, // Update to latest provider used
      // Keep track of linked accounts
      linked_accounts: JSON.stringify([
        ...existingLinkedAccounts,
        {
          provider: newUserData.provider,
          linked_at: new Date().toISOString(),
          original_id: existingProfile.id,
        },
      ]),
    };

    // Update the current user's profile with merged data
    const { data, error } = await supabase
      .from("profiles")
      .upsert(mergedData)
      .eq("id", currentUserId)
      .select()
      .single();

    if (error) {
      return { success: false, error: error.message };
    }

    // Archive the old profile (soft delete by marking as linked)
    await supabase
      .from("profiles")
      .update({
        linked_to: currentUserId,
        updated_at: new Date().toISOString(),
      })
      .eq("id", existingProfile.id);

    return { success: true, mergedProfile: data as ProfileData };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : "Unknown error",
    };
  }
};

// Helper to check if session is valid with proper typing and timeout
export const validateSession = async (): Promise<SessionValidationResult> => {
  // Only run on client side
  if (typeof window === "undefined") {
    return {
      isValid: false,
      session: null,
      error: "Server-side execution not allowed",
    };
  }

  if (!supabase.auth) {
    return {
      isValid: false,
      session: null,
      error: "Supabase client not available",
    };
  }

  try {
    // Create timeout promise
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error("Session validation timeout")), 6000);
    });

    // Create session validation promise
    const sessionPromise = supabase.auth.getSession();

    // Race between timeout and session validation
    const {
      data: { session },
      error,
    } = await Promise.race([sessionPromise, timeoutPromise]);

    if (error) {
      return { isValid: false, session: null, error: error.message };
    }

    if (!session) {
      return { isValid: false, session: null };
    }

    // Validate session structure and expiry
    if (!session.user || !session.access_token) {
      return {
        isValid: false,
        session: null,
        error: "Invalid session structure",
      };
    }

    // Check if session is expired
    const now = Math.floor(Date.now() / 1000);
    if (session.expires_at && session.expires_at <= now) {
      return {
        isValid: false,
        session: null,
        error: "Session expired",
      };
    }

    return { isValid: true, session };
  } catch (err) {
    if (err instanceof Error && err.message.includes("timeout")) {
      return {
        isValid: false,
        session: null,
        error: "Session validation timed out",
      };
    }

    return {
      isValid: false,
      session: null,
      error: err instanceof Error ? err.message : "Unknown validation error",
    };
  }
};

// Enhanced function to get user profile with timeout protection
export const getUserProfileWithLinking = async (
  user: SupabaseUser
): Promise<NormalizedUserData | null> => {
  if (
    !isValidSupabaseUser(user) ||
    typeof window === "undefined" ||
    !supabase.from
  ) {
    return null;
  }

  try {
    // Add timeout to prevent hanging profile loads
    const timeoutPromise = new Promise<null>((_, reject) => {
      setTimeout(() => reject(new Error("Profile load timeout")), 8000);
    });

    const profilePromise = (async () => {
      // First, try to get existing profile for current user
      const { data: currentProfile, error: profileError } = await supabase
        .from("profiles")
        .select("*")
        .eq("id", user.id)
        .single();

      if (!profileError && currentProfile && !currentProfile.linked_to) {
        // Profile exists and is active, return with normalization
        return getNormalizedUserData(user, currentProfile as ProfileData);
      }

      // If no profile exists or profile check failed, look for linkable accounts
      if (user.email) {
        const existingProfile = await findAndLinkAccounts(user.email, user.id);

        if (existingProfile) {
          // Found linkable account, merge the data
          const newUserData = getNormalizedUserData(user);
          if (!newUserData) {
            return null;
          }

          const linkingResult = await mergeProfileData(
            user.id,
            existingProfile,
            newUserData
          );

          if (linkingResult.success && linkingResult.mergedProfile) {
            return getNormalizedUserData(user, linkingResult.mergedProfile);
          }
        }
      }

      // No existing profile found, create new one or return normalized auth data
      const normalizedData = getNormalizedUserData(user);
      if (!normalizedData) {
        return null;
      }

      // Try to create profile entry with timeout
      try {
        await Promise.race([
          supabase.from("profiles").upsert({
            id: user.id,
            email: user.email || "",
            username: normalizedData.username,
            name: normalizedData.name,
            avatar_url: normalizedData.avatar_url,
            provider: normalizedData.provider,
          }),
          new Promise((_, reject) =>
            setTimeout(
              () => reject(new Error("Profile creation timeout")),
              3000
            )
          ),
        ]);
      } catch {
        // Silent handling of profile creation errors/timeouts
      }

      return normalizedData;
    })();

    return await Promise.race([profilePromise, timeoutPromise]);
  } catch {
    // If profile loading fails, fall back to basic user data
    return getNormalizedUserData(user);
  }
};

// Type-safe profile update function
export const updateUserProfile = async (
  userId: string,
  updates: ProfileUpdateData
): Promise<ProfileUpdateResult> => {
  if (typeof window === "undefined" || !supabase.from) {
    return { success: false, error: "Client-side only operation" };
  }

  try {
    const { data, error } = await supabase
      .from("profiles")
      .update(updates)
      .eq("id", userId)
      .select()
      .single();

    if (error) {
      return { success: false, error: error.message };
    }

    return { success: true, data: data as ProfileData };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : "Unknown update error",
    };
  }
};
