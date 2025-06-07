"use client";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";
import { toast } from "sonner";
import Script from "next/script";

declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void;
      execute: (
        siteKey: string,
        options: { action: string }
      ) => Promise<string>;
    };
  }
}

const SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

interface LoginFormProps {
  onLoginSuccess?: () => void;
}

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [mode, setMode] = useState<"login" | "register" | "forgot">("login");
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [recaptchaLoaded, setRecaptchaLoaded] = useState(false);
  const [forgotPasswordSuccess, setForgotPasswordSuccess] = useState(false);

  useEffect(() => {
    // Check if reCAPTCHA is already loaded
    if (window.grecaptcha) {
      setRecaptchaLoaded(true);
    } else {
      // Wait for the script to load
      const checkRecaptcha = setInterval(() => {
        if (window.grecaptcha) {
          setRecaptchaLoaded(true);
          clearInterval(checkRecaptcha);
        }
      }, 100);

      // Cleanup interval after 10 seconds
      setTimeout(() => clearInterval(checkRecaptcha), 10000);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const executeRecaptcha = (action: string = "submit"): Promise<string> => {
    return new Promise((resolve, reject) => {
      if (!SITE_KEY) {
        console.error("reCAPTCHA site key is missing");
        reject(new Error("reCAPTCHA configuration error"));
        return;
      }

      if (!window.grecaptcha) {
        console.error("reCAPTCHA script not loaded");
        reject(new Error("reCAPTCHA not loaded"));
        return;
      }

      if (!recaptchaLoaded) {
        console.error("reCAPTCHA still initializing");
        reject(new Error("reCAPTCHA still loading"));
        return;
      }

      window.grecaptcha.ready(() => {
        window.grecaptcha
          .execute(SITE_KEY as string, { action })
          .then((token) => {
            if (!token || token.length === 0) {
              console.error("Empty reCAPTCHA token received");
              reject(new Error("Empty reCAPTCHA token received"));
              return;
            }
            resolve(token);
          })
          .catch((error) => {
            console.error("reCAPTCHA execution failed:", error);
            reject(new Error("Failed to execute reCAPTCHA"));
          });
      });
    });
  };

  const handleForgotPassword = async () => {
    if (!formData.email) {
      toast.error("Please enter your email address");
      return;
    }

    if (!recaptchaLoaded) {
      toast.error(
        "Security verification is loading. Please wait a moment and try again."
      );
      return;
    }

    if (!SITE_KEY) {
      console.error("reCAPTCHA site key is missing from environment");
      toast.error(
        "Security verification is not configured. Please check configuration."
      );
      return;
    }

    setIsLoading(true);

    try {
      let token = "";
      try {
        token = await executeRecaptcha("forgot_password");
      } catch (error) {
        toast.error(
          "Security verification failed. Please refresh the page and try again."
        );
        console.error(error);
        setIsLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          recaptcha: token,
        }),
      });

      if (!response.ok) {
        let errorData;
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
          errorData = await response.json();
          throw new Error(errorData.message || "Failed to send reset email");
        } else {
          throw new Error(
            `Server error: ${response.status} - ${response.statusText}`
          );
        }
      }

      await response.json();
      setForgotPasswordSuccess(true);
      toast.success("Password reset email sent! Check your inbox.");
    } catch (error) {
      console.error("Password reset error:", error);
      toast.error(
        error instanceof Error ? error.message : "Failed to send reset email"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailPasswordSubmit = async (
    email: string,
    password: string,
    isRegister: boolean
  ) => {
    try {
      if (isRegister) {
        // Register with Supabase Auth
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/auth/callback?type=signup`,
          },
        });

        if (error) {
          // Check if user already exists with a different provider
          if (error.message.includes("already registered")) {
            toast.error(
              "An account with this email already exists. Try logging in or use 'Forgot Password' if you can't remember your credentials."
            );
            return;
          }
          throw error;
        }

        if (data.user && !data.session) {
          toast.success(
            "Registration successful! Please check your email to confirm your account."
          );
          setMode("login");
          setStep(1);
          setFormData({
            username: "",
            email: "",
            password: "",
            confirmPassword: "",
          });
        } else if (data.session) {
          // Auto-confirmed
          toast.success("Registration successful! You're now logged in.");
          onLoginSuccess?.();
        }
      } else {
        // Login with Supabase Auth
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) {
          // Provide helpful error messages
          if (error.message.includes("Invalid login credentials")) {
            toast.error(
              "Invalid email or password. Please check your credentials and try again."
            );
          } else if (error.message.includes("Email not confirmed")) {
            toast.error(
              "Please confirm your email address before logging in. Check your inbox for a confirmation link."
            );
          } else {
            toast.error(error.message || "Login failed");
          }
          return;
        }

        if (data.user) {
          toast.success(`Welcome back!`);
          onLoginSuccess?.();
        }
      }
    } catch (error) {
      console.error("Auth error:", error);
      toast.error(
        error instanceof Error ? error.message : "Authentication failed"
      );
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const redirectUrl = `${window.location.origin}/auth/callback`;

      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: redirectUrl,
          queryParams: {
            access_type: "offline",
            prompt: "consent",
          },
        },
      });

      if (error) {
        // Handle specific OAuth errors
        if (error.message.includes("popup_closed_by_user")) {
          toast.error("Sign-in was cancelled. Please try again.");
        } else {
          console.error("Google sign-in error:", error);
          toast.error("Google sign-in failed. Please try again.");
        }
      }
      // Success will be handled by the callback page
    } catch (error) {
      console.error("Google sign-in error:", error);
      toast.error("Google sign-in failed. Please try again.");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (mode === "forgot") {
      await handleForgotPassword();
      return;
    }

    setIsLoading(true);

    if (mode === "register" && step === 1) {
      if (formData.password !== formData.confirmPassword) {
        toast.error("Passwords do not match");
        setIsLoading(false);
        return;
      }
      setStep(2);
      setIsLoading(false);
      return;
    }

    // For email/password authentication, we'll use Supabase directly
    // instead of the backend API to avoid provider conflicts
    try {
      await handleEmailPasswordSubmit(
        formData.email,
        formData.password,
        mode === "register"
      );
    } catch (error) {
      console.error("Form submission error:", error);
      toast.error(
        error instanceof Error ? error.message : "Authentication error"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    });
    setStep(1);
    setForgotPasswordSuccess(false);
  };

  const switchMode = (newMode: "login" | "register" | "forgot") => {
    setMode(newMode);
    resetForm();
  };

  return (
    <>
      <Script
        src={`https://www.google.com/recaptcha/api.js?render=${SITE_KEY}`}
        strategy="afterInteractive"
        onLoad={() => {
          setRecaptchaLoaded(true);
        }}
        onError={() => {
          toast.error(
            "Failed to load security verification. Please refresh the page."
          );
        }}
      />

      <div className="w-96 rounded-lg flex flex-col items-center justify-center p-4 bg-gray-800">
        <div className="w-full max-w-md p-4 space-y-4">
          <h2 className="text-xl font-bold text-center">
            {mode === "login"
              ? "Welcome Back!"
              : mode === "register"
              ? step === 1
                ? "Create your account"
                : "Set up your username"
              : "Forgot Password"}
          </h2>

          {mode === "forgot" && (
            <p className="text-gray-400 text-sm text-center">
              {forgotPasswordSuccess
                ? "We've sent you a password reset link"
                : "Enter your email to receive a password reset link"}
            </p>
          )}

          {!recaptchaLoaded && (
            <div className="text-center text-sm text-yellow-400 bg-yellow-900 bg-opacity-20 p-2 rounded">
              Loading security verification...
            </div>
          )}

          {/* Forgot Password Success State */}
          {mode === "forgot" && forgotPasswordSuccess ? (
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
                    d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="text-center">
                <h3 className="text-green-400 font-medium mb-2">Email Sent!</h3>
                <p className="text-sm text-gray-400 mb-4">
                  We&apos;ve sent a password reset link to{" "}
                  <span className="text-white font-medium">
                    {formData.email}
                  </span>
                </p>
                <p className="text-xs text-gray-500">
                  Don&apos;t see the email? Check your spam folder or wait a few
                  minutes for it to arrive.
                </p>
              </div>
            </div>
          ) : (
            <form className="space-y-3" onSubmit={handleSubmit}>
              {mode === "register"
                ? step === 2 && (
                    <div>
                      <Label htmlFor="username" className="text-sm">
                        Username
                      </Label>
                      <Input
                        id="username"
                        type="text"
                        placeholder="Enter username"
                        required
                        className="text-white bg-gray-700 h-9"
                        value={formData.username}
                        onChange={handleChange}
                      />
                    </div>
                  )
                : null}
              {(mode === "login" || mode === "forgot" || step === 1) && (
                <>
                  <div>
                    <Label htmlFor="email" className="text-sm">
                      Email Address
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email address"
                      required
                      className="text-white bg-gray-700 h-9 border-gray-600 focus:border-blue-500 focus:ring-blue-500"
                      value={formData.email}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  </div>
                  {mode !== "forgot" && (
                    <>
                      <div>
                        <Label htmlFor="password" className="text-sm">
                          Password
                        </Label>
                        <Input
                          id="password"
                          type="password"
                          placeholder="Enter your password"
                          required
                          className="text-white bg-gray-700 h-9"
                          value={formData.password}
                          onChange={handleChange}
                        />
                      </div>
                      {mode === "register" && (
                        <div>
                          <Label htmlFor="confirmPassword" className="text-sm">
                            Confirm Password
                          </Label>
                          <Input
                            id="confirmPassword"
                            type="password"
                            placeholder="Confirm your password"
                            required
                            className="text-white bg-gray-700 h-9"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                          />
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
              <Button
                type="submit"
                className="w-full"
                disabled={isLoading || !recaptchaLoaded}
              >
                {isLoading ? (
                  <>
                    <span className="ml-2">
                      {mode === "forgot" ? "Sending..." : "Processing..."}
                    </span>
                  </>
                ) : !recaptchaLoaded ? (
                  "Loading..."
                ) : mode === "login" ? (
                  "Login"
                ) : mode === "forgot" ? (
                  "Send Reset Link"
                ) : step === 1 ? (
                  "Next"
                ) : (
                  "Sign Up"
                )}
              </Button>
            </form>
          )}

          {mode !== "forgot" && (
            <>
              <div className="flex items-center justify-center my-2 space-x-2">
                <div className="w-1/4 h-px bg-gray-600"></div>
                <p className="text-xs text-gray-400">OR</p>
                <div className="w-1/4 h-px bg-gray-600"></div>
              </div>
              <Button
                className="flex items-center justify-center w-full gap-2 p-1 text-black text-sm transition bg-white rounded-md shadow-md hover:!bg-gray-900 hover:text-white"
                onClick={handleGoogleSignIn}
                disabled={isLoading}
                type="button"
              >
                <Image
                  src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg"
                  alt="Google Logo"
                  className="w-4 h-4"
                  width={16}
                  height={16}
                />
                {mode === "login"
                  ? "Continue with Google"
                  : "Sign up with Google"}
              </Button>

              {/* Provider conflict warning */}
              <div className="text-xs text-gray-500 text-center">
                <p>
                  Note: Google and email logins create separate accounts even
                  with the same email.
                </p>
              </div>
            </>
          )}

          <div className="flex items-center justify-between text-xs">
            {mode === "login" ? (
              <>
                <button
                  type="button"
                  className="text-gray-400 hover:underline"
                  onClick={() => switchMode("forgot")}
                  disabled={isLoading}
                >
                  Forgot password?
                </button>
                <button
                  type="button"
                  className="text-gray-400 hover:underline"
                  onClick={() => switchMode("register")}
                  disabled={isLoading}
                >
                  Sign up
                </button>
              </>
            ) : mode === "register" ? (
              <>
                <span className="text-gray-500">Already have an account?</span>
                <button
                  type="button"
                  className="text-gray-400 hover:underline"
                  onClick={() => switchMode("login")}
                  disabled={isLoading}
                >
                  Login instead
                </button>
              </>
            ) : (
              <>
                <span className="text-gray-500">Remember your password?</span>
                <button
                  type="button"
                  className="text-gray-400 hover:underline"
                  onClick={() => switchMode("login")}
                  disabled={isLoading}
                >
                  Sign in instead
                </button>
              </>
            )}
          </div>

          {mode === "forgot" && forgotPasswordSuccess && (
            <button
              onClick={() => {
                setForgotPasswordSuccess(false);
                setFormData({ ...formData, email: "" });
              }}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors w-full text-center"
            >
              Try with a different email
            </button>
          )}
        </div>
      </div>
    </>
  );
}
