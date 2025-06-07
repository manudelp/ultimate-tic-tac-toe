"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase, getUserProfileWithLinking } from "@/lib/supabase";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";

// Force dynamic rendering to prevent prerendering
export const dynamic = "force-dynamic";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState("Processing authentication...");

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Check for error in URL params first
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        if (error) {
          console.error("Auth callback error:", error, errorDescription);
          toast.error(errorDescription || "Authentication failed");
          router.push("/");
          return;
        }

        setStatus("Verifying session...");

        // Get the current session
        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession();

        if (sessionError) {
          console.error("Session error:", sessionError);
          toast.error("Authentication failed");
          router.push("/");
          return;
        }

        if (!session) {
          setStatus("No active session found");
          toast.error("Authentication failed - no session");
          router.push("/");
          return;
        }

        setStatus("Setting up user profile...");

        // Get user profile with linking logic
        const userData = await getUserProfileWithLinking(session.user);

        if (!userData) {
          toast.error("Failed to process user data");
          router.push("/");
          return;
        }

        // Store user data for UI state management
        localStorage.setItem("userData", JSON.stringify(userData));

        // Handle different authentication flows
        const provider = userData.provider;

        if (provider === "google") {
          // Check if this was a newly linked account
          if (userData._originalAuthData) {
            toast.success(
              `Accounts linked! Welcome back, ${
                userData.name || userData.username
              }!`
            );
          } else {
            toast.success(
              `Welcome${userData.name ? `, ${userData.name}` : ""}!`
            );
          }
        } else {
          // Email confirmation or password reset
          const type = searchParams.get("type");
          if (type === "signup") {
            toast.success("Email confirmed! You're now logged in.");
          } else if (type === "recovery") {
            // Handle password reset confirmation
            const accessToken = searchParams.get("access_token");
            const refreshToken = searchParams.get("refresh_token");

            if (accessToken && refreshToken) {
              // Redirect to reset password page with tokens
              router.push(
                `/reset-password?access_token=${accessToken}&refresh_token=${refreshToken}`
              );
              return;
            } else {
              toast.success("Password reset confirmed! You're now logged in.");
            }
          } else {
            toast.success("Login successful!");
          }
        }

        setStatus("Redirecting...");

        // Small delay to ensure localStorage is written
        setTimeout(() => {
          router.push("/");
        }, 500);
      } catch (error) {
        console.error("Auth callback error:", error);
        toast.error("Authentication failed");
        router.push("/");
      }
    };

    handleAuthCallback();
  }, [router, searchParams]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Loader />
      <p className="text-gray-400 mt-4">{status}</p>
    </div>
  );
}

export default function Callback() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center min-h-screen">
          <Loader />
          <p className="text-gray-400 mt-4">Loading...</p>
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
