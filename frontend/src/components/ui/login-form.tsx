"use client";
import { useState, useEffect } from "react";
import { supabase, getUserProfileWithLinking } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";
import { toast } from "sonner";
import Script from "next/script";
import { LoginFormData, ValidationResult } from "@/types/auth";

declare global {
  interface Window {
    turnstile: {
      render: (
        container: string | HTMLElement,
        options: {
          sitekey: string;
          callback: (token: string) => void;
          "error-callback"?: () => void;
          theme?: string;
          size?: string;
        }
      ) => string;
      reset: (widgetId: string) => void;
      remove: (widgetId: string) => void;
    };
  }
}

const SITE_KEY = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

interface LoginFormProps {
  onLoginSuccess?: () => void;
}

type FormMode = "login" | "register" | "forgot";

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [mode, setMode] = useState<FormMode>("login");
  const [step, setStep] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [formData, setFormData] = useState<LoginFormData>({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [turnstileLoaded, setTurnstileLoaded] = useState<boolean>(false);
  const [turnstileWidgetId, setTurnstileWidgetId] = useState<string | null>(null);
  const [forgotPasswordSuccess, setForgotPasswordSuccess] =
    useState<boolean>(false);
  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});

  useEffect(() => {
    const checkTurnstile = setInterval(() => {
      if (window.turnstile) {
        setTurnstileLoaded(true);
        clearInterval(checkTurnstile);
      }
    }, 100);

    setTimeout(() => clearInterval(checkTurnstile), 10000);

    return () => clearInterval(checkTurnstile);
  }, []);

  useEffect(() => {
    if (turnstileLoaded && SITE_KEY && !turnstileWidgetId) {
      const container = document.getElementById('turnstile-container');
      if (container) {
        const id = window.turnstile.render(container, {
          sitekey: SITE_KEY,
          callback: (token: string) => setTurnstileToken(token),
          "error-callback": () => setTurnstileToken(null),
          theme: 'dark',
          size: 'flexible',
        });
        setTurnstileWidgetId(id);
      }
    }
  }, [turnstileLoaded, turnstileWidgetId]);

  const validateForm = (): ValidationResult => {
    const errors: Record<string, string> = {};

    if (mode !== "forgot") {
      if (!formData.email) {
        errors.email = "Email is required";
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        errors.email = "Invalid email format";
      }

      if (!formData.password) {
        errors.password = "Password is required";
      } else if (formData.password.length < 6) {
        errors.password = "Password must be at least 6 characters";
      }

      if (mode === "register") {
        if (!formData.username) {
          errors.username = "Username is required";
        } else if (formData.username.length < 3) {
          errors.username = "Username must be at least 3 characters";
        }

        if (formData.password !== formData.confirmPassword) {
          errors.confirmPassword = "Passwords do not match";
        }
      }
    } else {
      if (!formData.email) {
        errors.email = "Email is required";
      }
    }

    setValidationErrors(errors);
    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: value,
    }));

    // Clear validation error for this field
    if (validationErrors[id]) {
      setValidationErrors((prev) => ({
        ...prev,
        [id]: "",
      }));
    }
  };

  const resetTurnstile = () => {
    setTurnstileToken(null);
    if (turnstileWidgetId && window.turnstile) {
      window.turnstile.reset(turnstileWidgetId);
    }
  };

  const handleForgotPassword = async (): Promise<void> => {
    const validation = validateForm();
    if (!validation.isValid) {
      return;
    }

    if (!turnstileLoaded || !turnstileToken) {
      toast.error(
        "Please complete the security verification."
      );
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          turnstile: turnstileToken,
        }),
      });

      if (!response.ok) {
        const contentType = response.headers.get("content-type");
        let errorMessage = "Failed to send reset email";

        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          errorMessage = errorData.message || errorMessage;
        }

        throw new Error(errorMessage);
      }

      setForgotPasswordSuccess(true);
      toast.success("Password reset email sent! Check your inbox.");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to send reset email"
      );
    } finally {
      setIsLoading(false);
      resetTurnstile();
    }
  };

  const handleEmailPasswordSubmit = async (
    email: string,
    password: string,
    isRegister: boolean
  ): Promise<void> => {
    try {
      // Set operation timeout
      const operationTimeout = setTimeout(() => {
        setIsLoading(false);
        toast.error("Operation timed out. Please try again.");
      }, 15000);

      if (isRegister) {
        // Register with Supabase Auth
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/auth/callback?type=signup`,
            data: {
              username: formData.username,
              name: formData.username,
            },
          },
        });

        clearTimeout(operationTimeout);

        if (error) {
          if (error.message.includes("already registered")) {
            toast.error(
              "An account with this email already exists. Try logging in or use 'Forgot Password' if you can't remember your credentials."
            );
            return;
          }
          throw error;
        }

        if (data.user && !data.session) {
          // Handle account linking during registration with timeout
          try {
            const linkingTimeout = setTimeout(() => {
              toast.success(
                "Registration successful! Please check your email to confirm your account."
              );
            }, 5000);

            const linkedProfile = await getUserProfileWithLinking(data.user);
            clearTimeout(linkingTimeout);

            if (linkedProfile?._originalAuthData) {
              toast.success(
                "Account linked! Please check your email to confirm your account."
              );
            } else {
              toast.success(
                "Registration successful! Please check your email to confirm your account."
              );
            }
          } catch {
            toast.success(
              "Registration successful! Please check your email to confirm your account."
            );
          }

          setMode("login");
          setStep(1);
          setFormData({
            username: "",
            email: "",
            password: "",
            confirmPassword: "",
          });
        } else if (data.session) {
          // Auto-confirmed - handle linking with timeout
          try {
            const linkingTimeout = setTimeout(() => {
              toast.success("Registration successful! You're now logged in.");
              onLoginSuccess?.();
            }, 5000);

            const linkedProfile = await getUserProfileWithLinking(data.user!);
            clearTimeout(linkingTimeout);

            if (linkedProfile?._originalAuthData) {
              toast.success(
                "Accounts linked! Registration successful and you're now logged in."
              );
            } else {
              toast.success("Registration successful! You're now logged in.");
            }
          } catch {
            toast.success("Registration successful! You're now logged in.");
          }

          onLoginSuccess?.();
        }
      } else {
        // Login with Supabase Auth
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        clearTimeout(operationTimeout);

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

        if (data.user && data.session) {
          // Handle account linking during login with timeout
          try {
            const linkingTimeout = setTimeout(() => {
              toast.success("Welcome back!");
              onLoginSuccess?.();
            }, 5000);

            const linkedProfile = await getUserProfileWithLinking(data.user);
            clearTimeout(linkingTimeout);

            if (linkedProfile?._originalAuthData) {
              toast.success(
                `Accounts linked! Welcome back, ${
                  linkedProfile.name || linkedProfile.username
                }!`
              );
            } else {
              toast.success("Welcome back!");
            }
          } catch {
            toast.success("Welcome back!");
          }

          onLoginSuccess?.();
        }
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Authentication failed");
    }
  };

  const handleGoogleSignIn = async (): Promise<void> => {
    try {
      // Set operation timeout for OAuth
      const oauthTimeout = setTimeout(() => {
        setIsLoading(false);
        toast.error("Sign-in timed out. Please try again.");
      }, 10000);

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

      clearTimeout(oauthTimeout);

      if (error) {
        // Handle specific OAuth errors
        if (error.message.includes("popup_closed_by_user")) {
          toast.error("Sign-in was cancelled. Please try again.");
        } else {
          toast.error("Authentication failed. Please try again.");
        }
      }
      // Success will be handled by the callback page
    } catch {
      toast.error("Authentication failed. Please try again.");
    }
  };

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();

    if (mode === "forgot") {
      await handleForgotPassword();
      return;
    }

    const validation = validateForm();
    if (!validation.isValid) {
      toast.error("Please fix the errors in the form");
      return;
    }

    setIsLoading(true);

    if (mode === "register" && step === 1) {
      setStep(2);
      setIsLoading(false);
      return;
    }

    try {
      await handleEmailPasswordSubmit(
        formData.email,
        formData.password,
        mode === "register"
      );
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Authentication error");
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = (): void => {
    setFormData({
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    });
    setStep(1);
    setForgotPasswordSuccess(false);
    setValidationErrors({});
    resetTurnstile();
  };

  const switchMode = (newMode: FormMode): void => {
    setMode(newMode);
    resetForm();
  };

  return (
    <>
      <Script
        src="https://challenges.cloudflare.com/turnstile/v0/api.js"
        strategy="afterInteractive"
        onLoad={() => setTurnstileLoaded(true)}
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

          {!turnstileLoaded && (
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
                      {validationErrors.username && (
                        <p className="text-red-500 text-xs mt-1">
                          {validationErrors.username}
                        </p>
                      )}
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
                      className={`text-white bg-gray-700 h-9 border-gray-600 focus:border-blue-500 focus:ring-blue-500 ${
                        validationErrors.email ? "border-red-500" : ""
                      }`}
                      value={formData.email}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                    {validationErrors.email && (
                      <p className="text-red-500 text-xs mt-1">
                        {validationErrors.email}
                      </p>
                    )}
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
                        {validationErrors.password && (
                          <p className="text-red-500 text-xs mt-1">
                            {validationErrors.password}
                          </p>
                        )}
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
                          {validationErrors.confirmPassword && (
                            <p className="text-red-500 text-xs mt-1">
                              {validationErrors.confirmPassword}
                            </p>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
              <div id="turnstile-container" className="flex justify-center" />
              <Button
                type="submit"
                className="w-full"
                disabled={isLoading || !turnstileToken}
              >
                {isLoading ? (
                  <span className="ml-2">
                    {mode === "forgot" ? "Sending..." : "Processing..."}
                  </span>
                ) : !turnstileLoaded ? (
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
