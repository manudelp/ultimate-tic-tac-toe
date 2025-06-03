"use client";
import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";
import { toast } from "sonner";
import { loginUser, registerUser, verifyToken } from "@/api";
import { reconnectSocket } from "@/socket";
import Script from "next/script";

const SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;

// Add type declaration for grecaptcha
declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void;
      execute: (
        siteKey: string,
        options: { action: string }
      ) => Promise<string>;
      render: (container: string | HTMLElement, parameters: object) => number;
      reset: (widgetId?: number) => void;
      getResponse: (widgetId?: number) => string;
    };
    onRecaptchaLoad: (() => void) | undefined;
  }
}

interface LoginFormProps {
  onLoginSuccess?: () => void;
}

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [recaptchaToken, setRecaptchaToken] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const recaptchaRef = useRef<HTMLDivElement>(null);
  const recaptchaWidgetId = useRef<number | null>(null);

  // Define the onRecaptchaLoad function
  useEffect(() => {
    window.onRecaptchaLoad = () => {
      console.info("reCAPTCHA has loaded");
    };
    return () => {
      window.onRecaptchaLoad = () => {}; // Empty function instead of undefined
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  // Initialize reCAPTCHA when the component mounts
  useEffect(() => {
    // Reset any existing token
    setRecaptchaToken("");

    if (recaptchaRef.current && window.grecaptcha && SITE_KEY) {
      try {
        // Reset any existing widget
        if (recaptchaWidgetId.current !== null) {
          window.grecaptcha.reset(recaptchaWidgetId.current);
        }
        recaptchaWidgetId.current = window.grecaptcha.render(
          recaptchaRef.current,
          {
            sitekey: SITE_KEY,
            theme: "dark",
            callback: (token: string) => {
              setRecaptchaToken(token);
            },
            "expired-callback": () => {
              setRecaptchaToken("");
            },
          }
        );
      } catch (error) {
        console.error("Error rendering reCAPTCHA:", error);
      }
    }
    return () => {
      // Reset the reCAPTCHA widget when component unmounts
      if (recaptchaWidgetId.current !== null) {
        window.grecaptcha.reset(recaptchaWidgetId.current);
      }
    };
  }, [isLogin]); // Re-initialize when switching between login/register

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!recaptchaToken) {
      toast.error("Please complete the reCAPTCHA verification");
      return;
    }

    setIsLoading(true);

    try {
      if (isLogin) {
        // Login
        const { name } = await loginUser(
          formData.email,
          formData.password,
          recaptchaToken
        );

        // Verify the token to get complete user data
        await verifyToken();

        // Reconnect socket with the new auth token
        reconnectSocket();

        toast.success(`Welcome back, ${name}!`);

        // Call the success callback if provided
        if (onLoginSuccess) {
          onLoginSuccess();
        }
      } else {
        // Register
        if (formData.password !== formData.confirmPassword) {
          toast.error("Passwords do not match!");
          return;
        }

        const response = await registerUser(
          formData.username,
          formData.email,
          formData.password,
          recaptchaToken
        );
        toast.success(response.message);
        setIsLogin(true);
      }
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error("Something went wrong!");
      }
    } finally {
      setIsLoading(false);
      // Reset the reCAPTCHA
      if (window.grecaptcha && recaptchaWidgetId.current !== null) {
        window.grecaptcha.reset(recaptchaWidgetId.current);
        setRecaptchaToken("");
      }
    }
  };

  return (
    <>
      <Script
        src={`https://www.google.com/recaptcha/api.js?onload=onRecaptchaLoad&render=explicit`}
        strategy="lazyOnload"
      />
      <div className="w-96 rounded-lg flex flex-col items-center justify-center p-4 bg-gray-800">
        <div className="w-full max-w-md p-4 space-y-6">
          <h2 className="text-2xl font-bold text-center">
            {isLogin ? "Welcome Back!" : "Create Your Account"}
          </h2>
          <form className="space-y-4" onSubmit={handleSubmit}>
            {!isLogin && (
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  required
                  className="text-white bg-gray-700"
                  value={formData.username}
                  onChange={handleChange}
                />
              </div>
            )}
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                required
                className="text-white bg-gray-700"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                required
                className="text-white bg-gray-700"
                value={formData.password}
                onChange={handleChange}
              />
            </div>
            {!isLogin && (
              <div>
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Confirm your password"
                  required
                  className="text-white bg-gray-700"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
              </div>
            )}

            {/* Add the reCAPTCHA container */}
            <div className="flex justify-center my-4">
              <div ref={recaptchaRef}></div>
            </div>

            <Button type="submit" className="w-full mt-4" disabled={isLoading}>
              {isLoading ? "Processing..." : isLogin ? "Login" : "Sign Up"}
            </Button>
          </form>

          {/* Separador visual */}
          <div className="flex items-center justify-center my-4 space-x-2">
            <div className="w-1/4 h-px bg-gray-600"></div>
            <p className="text-sm text-gray-400">OR</p>
            <div className="w-1/4 h-px bg-gray-600"></div>
          </div>

          {/* Google Sign-In */}
          <Button
            className="flex items-center justify-center w-full gap-2 p-2 text-black transition bg-white rounded-md shadow-md hover:!bg-gray-900 hover:text-white"
            onClick={() => toast.info("Google Sign-In is coming soon!")}
            disabled={isLoading}
          >
            <Image
              src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg"
              alt="Google Logo"
              className="w-5 h-5"
              width={20}
              height={20}
            />
            {isLogin ? "Continue with Google" : "Sign up with Google"}
          </Button>

          <div className="flex items-center justify-between">
            <a href="#" className="text-sm text-gray-400 hover:underline">
              Forgot your password?
            </a>
            <button
              type="button"
              className="text-sm text-gray-400 hover:underline"
              onClick={() => setIsLogin(!isLogin)}
              disabled={isLoading}
            >
              {isLogin ? "  Sign up" : "Login instead"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
