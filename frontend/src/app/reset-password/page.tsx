"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { supabase } from "@/lib/supabase";
import Link from "next/link";

function ResetPasswordForm() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const hash = window.location.hash;
    const params = new URLSearchParams(hash.slice(1));
    const token =
      params.get("access_token") || searchParams.get("access_token");
    const refreshToken =
      params.get("refresh_token") || searchParams.get("refresh_token");

    if (token) {
      setAccessToken(token);

      // If we have both tokens, set the session
      if (refreshToken) {
        supabase.auth
          .setSession({
            access_token: token,
            refresh_token: refreshToken,
          })
          .then(({ error }) => {
            if (error) {
              toast.error("Invalid reset link");
              setTimeout(() => router.push("/"), 3000);
            }
          });
      }
    } else {
      toast.error("Invalid or missing reset token");
      setTimeout(() => router.push("/"), 3000);
    }
  }, [router, searchParams]);

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
      toast.error("Password must be at least 6 characters");
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
      const { error } = await supabase.auth.updateUser({ password });
      if (error) throw error;

      setIsSuccess(true);
      toast.success("Password updated successfully!");

      // Give time for the success message before redirecting
      setTimeout(() => router.push("/"), 3000);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Reset failed");
    } finally {
      setIsLoading(false);
    }
  };

  if (!accessToken) {
    return (
      <div className="text-center text-white">Invalid link. Redirecting...</div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-8">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg border border-gray-700">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-2">Reset Password</h1>
          <p className="text-gray-400 text-sm">
            {isSuccess
              ? "Your password has been updated successfully"
              : "Enter your new password below"}
          </p>
        </div>

        {isSuccess ? (
          <div className="text-center text-green-400">
            Password updated. Redirecting...
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
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
            <div>
              <Label
                htmlFor="confirmPassword"
                className="text-sm text-gray-300"
              >
                Confirm Password
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Updating..." : "Update Password"}
            </Button>
          </form>
        )}

        <div className="pt-4">
          <Link href="/">
            <Button variant="outline" className="w-full">
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function ResetPasswordClient() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center text-white">Loading...</div>
        </div>
      }
    >
      <ResetPasswordForm />
    </Suspense>
  );
}
