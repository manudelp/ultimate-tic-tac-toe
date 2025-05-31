"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";
import { toast } from "sonner";
import { loginUser, registerUser, verifyToken } from "@/api";
import { reconnectSocket } from "@/socket";

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
    };
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  useEffect(() => {
    const loadRecaptcha = () => {
      if (!window.grecaptcha || !SITE_KEY) return;
      window.grecaptcha.ready(() => {
        window.grecaptcha
          .execute(SITE_KEY, { action: "login" })
          .then(setRecaptchaToken);
      });
    };
    loadRecaptcha();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
    }
  };

  return (
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

          <Button
            type="submit"
            className="w-full mt-4 text-white bg-gray-700"
            disabled={isLoading}
          >
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
  );
}
