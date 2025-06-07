"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { supabase } from "@/lib/supabase";
import Loader from "@/components/ui/loader";
import Link from "next/link";

// Force dynamic rendering
export const dynamic = "force-dynamic";

export default function ResetPassword() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return;

    // Get access token from URL hash or search params
    const hash = window.location.hash;
    const params = new URLSearchParams(hash.slice(1));
    const token =
      params.get("access_token") || searchParams.get("access_token");

    if (token) {
      setAccessToken(token);
    } else {
      toast.error("Invalid or missing reset token");
      setTimeout(() => router.push("/"), 3000);
    }
  }, [isClient, router, searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!password || !confirmPassword) {
      toast.error("Please fill in all fields");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      toast.error("Password must be at least 6 characters long");
      return;
    }

    if (!accessToken) {
      toast.error("Invalid reset token");
      return;
    }

    if (!supabase) {
      toast.error("Service temporarily unavailable");
      return;
    }

    setIsLoading(true);

    try {
      // Update password using Supabase
      const { error } = await supabase.auth.updateUser({
        password: password,
      });

      if (error) {
        throw error;
      }

      setIsSuccess(true);
      toast.success("Password updated successfully!");

      // Redirect to login page after 3 seconds
      setTimeout(() => {
        router.push("/");
      }, 3000);
    } catch (error) {
      console.error("Password reset error:", error);
      toast.error(
        error instanceof Error ? error.message : "Failed to reset password"
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!isClient) {
    return null; // Prevent SSR issues
  }

  if (!accessToken) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen px-4 py-8">
        <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg border border-gray-700">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-white mb-2">Invalid Link</h1>
            <p className="text-gray-400">
              This password reset link is invalid or has expired.
            </p>
          </div>
          <Link href="/" className="w-full">
            <Button variant="outline" className="w-full">
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-8">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg border border-gray-700">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-2">Reset Password</h1>
          <p className="text-gray-400 text-sm">
            {isSuccess
              ? "Your password has been updated successfully"
              : "Enter your new password below"}
          </p>
        </div>

        {/* Content */}
        {isSuccess ? (
          <div className="flex flex-col items-center space-y-4">
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
              <h3 className="text-green-400 font-medium mb-2">
                Password Updated!
              </h3>
              <p className="text-sm text-gray-400 mb-4">
                Your password has been successfully updated. You can now log in
                with your new password.
              </p>
              <p className="text-xs text-gray-500">
                Redirecting you to the login page...
              </p>
            </div>
          </div>
        ) : (
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <Label htmlFor="password" className="text-sm text-gray-300">
                New Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your new password"
                required
                className="text-white bg-gray-700 border-gray-600 focus:border-blue-500 focus:ring-blue-500"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                minLength={6}
              />
            </div>

            <div>
              <Label
                htmlFor="confirmPassword"
                className="text-sm text-gray-300"
              >
                Confirm New Password
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your new password"
                required
                className="text-white bg-gray-700 border-gray-600 focus:border-blue-500 focus:ring-blue-500"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
                minLength={6}
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader />
                  <span className="ml-2">Updating Password...</span>
                </>
              ) : (
                "Update Password"
              )}
            </Button>
          </form>
        )}

        {/* Navigation */}
        <div className="flex flex-col space-y-3 pt-4 border-t border-gray-700">
          <Link href="/" className="w-full">
            <Button variant="outline" className="w-full">
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
