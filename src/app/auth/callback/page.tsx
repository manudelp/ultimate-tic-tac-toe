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
      // Set overall timeout for callback processing
      const callbackTimeout = setTimeout(() => {
        toast.error("Authentication processing timed out");
        router.push("/");
      }, 15000);

      try {
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        if (error) {
          clearTimeout(callbackTimeout);
          toast.error(errorDescription || "Authentication failed");
          router.push("/");
          return;
        }

        setStatus("Verifying session...");

        // Add timeout to session verification
        const sessionTimeout = setTimeout(() => {
          clearTimeout(callbackTimeout);
          toast.error("Session verification timed out");
          router.push("/");
        }, 8000);

        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession();

        clearTimeout(sessionTimeout);

        if (sessionError) {
          clearTimeout(callbackTimeout);
          toast.error("Authentication failed");
          router.push("/");
          return;
        }

        if (!session) {
          clearTimeout(callbackTimeout);
          setStatus("No active session found");
          toast.error("Authentication failed - no session");
          router.push("/");
          return;
        }

        setStatus("Setting up user profile...");

        // Add timeout to profile setup
        const profileTimeout = setTimeout(() => {
          clearTimeout(callbackTimeout);
          // Continue anyway if profile loading times out
          localStorage.setItem(
            "userData",
            JSON.stringify({
              id: session.user.id,
              email: session.user.email,
              name:
                session.user.user_metadata?.full_name ||
                session.user.email?.split("@")[0],
              username:
                session.user.user_metadata?.user_name ||
                session.user.email?.split("@")[0],
              avatar_url: session.user.user_metadata?.avatar_url || "",
            })
          );
          toast.success("Welcome! You're now logged in.");
          router.push("/");
        }, 10000);

        const userData = await getUserProfileWithLinking(session.user);
        clearTimeout(profileTimeout);

        if (!userData) {
          clearTimeout(callbackTimeout);
          toast.error("Failed to process user data");
          router.push("/");
          return;
        }

        localStorage.setItem("userData", JSON.stringify(userData));

        // Handle different authentication flows uniformly
        const type = searchParams.get("type");
        if (type === "signup") {
          toast.success("Email confirmed! You're now logged in.");
        } else if (type === "recovery") {
          const accessToken = searchParams.get("access_token");
          const refreshToken = searchParams.get("refresh_token");

          if (accessToken && refreshToken) {
            clearTimeout(callbackTimeout);
            router.push(
              `/reset-password?access_token=${accessToken}&refresh_token=${refreshToken}`
            );
            return;
          } else {
            toast.success("Password reset confirmed! You're now logged in.");
          }
        } else {
          // Check if this was a newly linked account - no provider exposure
          if (userData._originalAuthData) {
            toast.success(
              `Welcome back, ${userData.name || userData.username}!`
            );
          } else {
            toast.success("Welcome! You're now logged in.");
          }
        }

        setStatus("Redirecting...");
        clearTimeout(callbackTimeout);

        setTimeout(() => {
          router.push("/");
        }, 500);
      } catch {
        clearTimeout(callbackTimeout);
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
