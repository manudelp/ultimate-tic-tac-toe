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
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        if (error) {
          console.error("Auth callback error:", error, errorDescription);
          toast.error(errorDescription || "Authentication failed");
          router.push("/");
          return;
        }

        setStatus("Verifying session...");

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

        const userData = await getUserProfileWithLinking(session.user);

        if (!userData) {
          toast.error("Failed to process user data");
          router.push("/");
          return;
        }

        localStorage.setItem("userData", JSON.stringify(userData));

        // Handle different authentication flows without provider references
        const type = searchParams.get("type");
        if (type === "signup") {
          toast.success("Email confirmed! You're now logged in.");
        } else if (type === "recovery") {
          const accessToken = searchParams.get("access_token");
          const refreshToken = searchParams.get("refresh_token");

          if (accessToken && refreshToken) {
            router.push(
              `/reset-password?access_token=${accessToken}&refresh_token=${refreshToken}`
            );
            return;
          } else {
            toast.success("Password reset confirmed! You're now logged in.");
          }
        } else {
          // Check if this was a newly linked account
          if (userData._originalAuthData) {
            toast.success(
              `Welcome back, ${userData.name || userData.username}!`
            );
          } else {
            toast.success("Welcome! You're now logged in.");
          }
        }

        setStatus("Redirecting...");

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
