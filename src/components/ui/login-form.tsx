"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";
import { toast } from "sonner";
import { loginUser, registerUser } from "@/api";
import { reconnectSocket } from "@/socket";
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

interface LoginFormProps {
  onLoginSuccess?: () => void;
}

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [recaptchaLoaded, setRecaptchaLoaded] = useState(false);

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

  const executeRecaptcha = (): Promise<string> => {
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
          .execute(SITE_KEY as string, { action: "submit" })
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsLoading(true);

    if (!isLogin && step === 1) {
      if (formData.password !== formData.confirmPassword) {
        toast.error("Passwords do not match");
        setIsLoading(false);
        return;
      }
      setStep(2);
      setIsLoading(false);
      return;
    }

    if (!recaptchaLoaded) {
      toast.error(
        "Security verification is loading. Please wait a moment and try again."
      );
      setIsLoading(false);
      return;
    }

    if (!SITE_KEY) {
      console.error("reCAPTCHA site key is missing from environment");
      toast.error(
        "Security verification is not configured. Please check configuration."
      );
      setIsLoading(false);
      return;
    }

    try {
      let token = "";
      try {
        token = await executeRecaptcha();
      } catch (error) {
        toast.error(
          "Security verification failed. Please refresh the page and try again."
        );
        console.error(error);
        setIsLoading(false);
        return;
      }

      if (isLogin) {
        const result = await loginUser(
          formData.email,
          formData.password,
          token
        );
        reconnectSocket();
        toast.success(
          `Welcome back, ${result.user.name || result.user.username}!`
        );
        onLoginSuccess?.();
      } else {
        try {
          await registerUser(
            formData.email,
            formData.password,
            formData.username,
            token
          );
          toast.success("Registration complete. Please log in.");
          setIsLogin(true);
          setStep(1);
          setFormData({
            username: "",
            email: "",
            password: "",
            confirmPassword: "",
          });
        } catch (error) {
          console.error("Registration error:", error);
          if (error instanceof Error && error.message.includes("Supabase")) {
            toast.error("Failed to register user. Please try again later.");
          } else if (
            error instanceof Error &&
            error.message.includes("email")
          ) {
            toast.error(
              "Email is already in use. Please use a different email."
            );
          } else if (
            error instanceof Error &&
            error.message.includes("username")
          ) {
            toast.error(
              "Username is already taken. Please choose a different username."
            );
          } else {
            toast.error(
              error instanceof Error ? error.message : "Registration failed"
            );
          }
        }
      }
    } catch (error) {
      console.error("Form submission error:", error);
      toast.error(
        error instanceof Error ? error.message : "Authentication error"
      );
    } finally {
      setIsLoading(false);
    }
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
            {isLogin
              ? "Welcome Back!"
              : step === 1
              ? "Create your account"
              : "Set up your username"}
          </h2>

          {!recaptchaLoaded && (
            <div className="text-center text-sm text-yellow-400 bg-yellow-900 bg-opacity-20 p-2 rounded">
              Loading security verification...
            </div>
          )}

          <form className="space-y-3" onSubmit={handleSubmit}>
            {isLogin
              ? null
              : step === 2 && (
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
                )}
            {(isLogin || step === 1) && (
              <>
                <div>
                  <Label htmlFor="email" className="text-sm">
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    required
                    className="text-white bg-gray-700 h-9"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </div>
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
                {!isLogin && (
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
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || !recaptchaLoaded}
            >
              {isLoading
                ? "Processing..."
                : !recaptchaLoaded
                ? "Loading..."
                : isLogin
                ? "Login"
                : step === 1
                ? "Next"
                : "Sign Up"}
            </Button>
          </form>

          <div className="flex items-center justify-center my-2 space-x-2">
            <div className="w-1/4 h-px bg-gray-600"></div>
            <p className="text-xs text-gray-400">OR</p>
            <div className="w-1/4 h-px bg-gray-600"></div>
          </div>

          <Button
            className="flex items-center justify-center w-full gap-2 p-1 text-black text-sm transition bg-white rounded-md shadow-md hover:!bg-gray-900 hover:text-white"
            onClick={() => toast.info("Google Sign-In coming soon")}
            disabled={isLoading}
          >
            <Image
              src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg"
              alt="Google Logo"
              className="w-4 h-4"
              width={16}
              height={16}
            />
            {isLogin ? "Continue with Google" : "Sign up with Google"}
          </Button>

          <div className="flex items-center justify-between text-xs">
            <a href="#" className="text-gray-400 hover:underline">
              Forgot password?
            </a>
            <button
              type="button"
              className="text-gray-400 hover:underline"
              onClick={() => {
                setIsLogin(!isLogin);
                setStep(1);
              }}
              disabled={isLoading}
            >
              {isLogin ? "Sign up" : "Login instead"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
