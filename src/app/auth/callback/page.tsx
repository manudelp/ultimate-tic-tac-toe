"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase, getNormalizedUserData } from "@/lib/supabase";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";

export default function Callback() {
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

        // Get normalized user data
        const userData = getNormalizedUserData(session.user);

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
          // For Google OAuth, check if we need to create/update profile
          try {
            const { data: existingProfile } = await supabase
              .from("profiles")
              .select("*")
              .eq("id", userData.id)
              .single();

            if (!existingProfile) {
              // Create profile for new Google user
              const { error: profileError } = await supabase
                .from("profiles")
                .insert({
                  id: userData.id,
                  email: userData.email,
                  username: userData.username,
                  name: userData.name,
                  avatar_url: userData.avatar_url,
                  provider: "google",
                });

              if (profileError) {
                console.warn("Profile creation failed:", profileError);
                // Continue anyway - profile might already exist
              }
            }
          } catch (profileError) {
            console.warn("Profile check/creation failed:", profileError);
            // Continue anyway
          }

          toast.success(`Welcome${userData.name ? `, ${userData.name}` : ""}!`);
        } else {
          // Email confirmation or password reset
          const type = searchParams.get("type");
          if (type === "signup") {
            toast.success("Email confirmed! You're now logged in.");
          } else if (type === "recovery") {
            toast.success("Password reset confirmed! You're now logged in.");
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
