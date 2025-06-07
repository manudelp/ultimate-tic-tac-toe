"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";
import Button from "@/components/ui/button-2";
import Link from "next/link";

// Force dynamic rendering
export const dynamic = "force-dynamic";

export default function Confirm() {
  const [status, setStatus] = useState("Verifying your account...");
  const [isLoading, setIsLoading] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return;

    const handleConfirmation = async () => {
      try {
        // Check if Supabase is available
        if (!supabase) {
          setStatus("Service temporarily unavailable");
          setIsLoading(false);
          toast.error("Service temporarily unavailable");
          return;
        }

        const hash = window.location.hash;
        const params = new URLSearchParams(hash.slice(1)); // remove '#'
        const accessToken = params.get("access_token");
        const type = params.get("type");

        if (!accessToken || type !== "signup") {
          setStatus("Invalid or expired confirmation link");
          setIsLoading(false);
          toast.error("Invalid or expired confirmation link");
          return;
        }

        // Verify the token with Supabase
        const { data, error } = await supabase.auth.getUser(accessToken);

        if (error || !data?.user) {
          setStatus("Invalid or expired token");
          setIsLoading(false);
          toast.error("Invalid or expired token");
        } else {
          setStatus("Account confirmed successfully!");
          setIsSuccess(true);
          setIsLoading(false);
          toast.success("Account confirmed! You can now log in.");

          // Redirect to home page after 3 seconds
          setTimeout(() => {
            router.push("/");
          }, 3000);
        }
      } catch (error) {
        console.error("Confirmation error:", error);
        setStatus("An error occurred during verification");
        setIsLoading(false);
        toast.error("An error occurred during verification");
      }
    };

    handleConfirmation();
  }, [isClient, router]);

  if (!isClient) {
    return null; // Prevent SSR issues
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-8">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg border border-gray-700">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-2">
            Account Confirmation
          </h1>
          <p className="text-gray-400">
            {isLoading ? "Please wait while we verify your account..." : ""}
          </p>
        </div>

        {/* Status Content */}
        <div className="flex flex-col items-center space-y-4">
          {isLoading ? (
            <>
              <Loader />
              <p className="text-center text-gray-300">{status}</p>
            </>
          ) : isSuccess ? (
            <>
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div className="text-center">
                <p className="text-green-400 font-medium mb-2">{status}</p>
                <p className="text-sm text-gray-400">
                  Redirecting you to the home page...
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <div className="text-center">
                <p className="text-red-400 font-medium mb-2">{status}</p>
                <p className="text-sm text-gray-400">
                  Please check your email for a new confirmation link or try
                  registering again.
                </p>
              </div>
            </>
          )}
        </div>

        {/* Action Buttons */}
        {!isLoading && (
          <div className="flex flex-col items-center space-y-3">
            <Link href="/">
              <Button
                text="Go to Home Page"
                variant={isSuccess ? "success" : "danger"}
              />
            </Link>
          </div>
        )}

        {/* Help Text */}
        <div className="text-center text-xs text-gray-500">
          <p>
            Having trouble? Check if you find the confirmation email in your
            spam folder.
          </p>
        </div>
      </div>
    </div>
  );
}
