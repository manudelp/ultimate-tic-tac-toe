import {
  User as SupabaseUser,
  Session as SupabaseSession,
} from "@supabase/supabase-js";

// Core authentication types
export interface UserMetadata {
  full_name?: string;
  name?: string;
  user_name?: string;
  username?: string;
  avatar_url?: string;
  email?: string;
}

export interface AppMetadata {
  provider?: string;
  providers?: string[];
}

// Enhanced User type with strict typing
export interface TypedSupabaseUser
  extends Omit<SupabaseUser, "user_metadata" | "app_metadata"> {
  user_metadata: UserMetadata;
  app_metadata: AppMetadata;
}

// Database profile structure
export interface ProfileData {
  id: string;
  email: string;
  username: string;
  name: string;
  avatar_url: string;
  provider: "google" | "email";
  linked_accounts?: string; // JSON string
  linked_to?: string;
  created_at?: string;
  updated_at?: string;
}

// Normalized user data for application state
export interface NormalizedUserData {
  id: string;
  email: string;
  name: string;
  username: string;
  avatar_url: string;
  provider: "google" | "email";
  emailVerified: boolean;
  _originalAuthData?: NormalizedUserData;
}

// UI user state - removed provider and emailVerified from UI
export interface UIUserData {
  name: string;
  username: string;
  image: string;
}

// Account linking types
export interface LinkedAccount {
  provider: "google" | "email";
  linked_at: string;
  original_id: string;
}

export interface AccountLinkingResult {
  success: boolean;
  mergedProfile?: ProfileData;
  error?: string;
}

// Auth state management
export interface AuthState {
  user: UIUserData | null;
  isLoading: boolean;
  sessionChecked: boolean;
  error: string | null;
}

// Form validation
export interface LoginFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

// Session validation
export interface SessionValidationResult {
  isValid: boolean;
  session: SupabaseSession | null;
  error?: string;
}

// Profile update operations
export interface ProfileUpdateData {
  name?: string;
  username?: string;
  avatar_url?: string;
}

export interface ProfileUpdateResult {
  success: boolean;
  data?: ProfileData;
  error?: string;
}
