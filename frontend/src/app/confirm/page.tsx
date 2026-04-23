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
  const [status, setStatus] = useState("Verifying your request...");
  const [isLoading, setIsLoading] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [type, setType] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return;

    const handleConfirmation = async () => {
      try {
        if (!supabase) {
          setStatus("Service temporarily unavailable");
          setIsLoading(false);
          toast.error("Service temporarily unavailable");
          return;
        }

        const hash = window.location.hash;
        const params = new URLSearchParams(hash.slice(1)); // remove '#'

        const urlError = params.get("error");
        const errorCode = params.get("error_code");
        const errorDescription = params.get("error_description");

        if (urlError) {
          if (errorCode === "otp_expired") {
            setStatus("Link has expired");
          } else {
            setStatus(
              errorDescription?.replace(/\+/g, " ") || "Verification failed"
            );
          }
          setIsLoading(false);
          toast.error(
            errorDescription?.replace(/\+/g, " ") || "Verification failed"
          );
          return;
        }

        const accessToken = params.get("access_token");
        const typeParam = params.get("type");
        setType(typeParam);

        if (
          !accessToken ||
          (typeParam !== "signup" && typeParam !== "recovery")
        ) {
          setStatus("Invalid or expired link");
          setIsLoading(false);
          toast.error("Invalid or expired link");
          return;
        }

        const { data, error } = await supabase.auth.getUser(accessToken);

        if (error || !data?.user) {
          setStatus("Invalid or expired token");
          setIsLoading(false);
          toast.error("Invalid or expired token");
          return;
        }

        if (typeParam === "signup") {
          setStatus("Account confirmed successfully!");
          setIsSuccess(true);
          setIsLoading(false);
          toast.success("Account confirmed! You can now log in.");
          setTimeout(() => router.push("/"), 3000);
        } else if (typeParam === "recovery") {
          setStatus(
            "Password reset link verified. You can now reset your password."
          );
          setIsSuccess(true);
          setIsLoading(false);
          // Redirect to password reset page or show password reset UI here
          setTimeout(() => router.push("/reset-password"), 3000);
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

  if (!isClient) return null;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-8">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg border border-gray-700">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-2">
            {type === "signup"
              ? "Account Confirmation"
              : "Password Reset Confirmation"}
          </h1>
          <p className="text-gray-400">{isLoading ? status : ""}</p>
        </div>

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
                  Redirecting you to the{" "}
                  {type === "signup" ? "home page" : "password reset page"}...
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
                  Check your email for a new link or try again.
                </p>
              </div>
            </>
          )}

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

          <div className="text-center text-xs text-gray-500">
            <p>Having trouble? Check your spam folder.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
