// src/components/ui/login-form.tsx
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
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const recaptchaRef = useRef<HTMLDivElement>(null);
  const recaptchaWidgetId = useRef<number | null>(null);

  useEffect(() => {
    window.onRecaptchaLoad = () => {
      if (recaptchaRef.current && window.grecaptcha && SITE_KEY) {
        setTimeout(() => initializeRecaptcha(), 100);
      }
    };
    return () => {
      window.onRecaptchaLoad = () => {};
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  useEffect(() => {
    setRecaptchaToken("");
    if (
      !recaptchaWidgetId.current &&
      recaptchaRef.current &&
      window.grecaptcha &&
      SITE_KEY
    ) {
      try {
        recaptchaWidgetId.current = window.grecaptcha.render(
          recaptchaRef.current,
          {
            sitekey: SITE_KEY,
            theme: "dark",
            callback: (token: string) => setRecaptchaToken(token),
            "expired-callback": () => setRecaptchaToken(""),
          }
        );
      } catch {
        // ignore
      }
    } else if (recaptchaWidgetId.current !== null && window.grecaptcha) {
      window.grecaptcha.reset(recaptchaWidgetId.current);
    }
    return () => {
      if (recaptchaWidgetId.current !== null && window.grecaptcha) {
        window.grecaptcha.reset(recaptchaWidgetId.current);
      }
    };
  }, [isLogin]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recaptchaToken) {
      toast.error("Complete reCAPTCHA");
      return;
    }
    setIsLoading(true);
    try {
      if (isLogin) {
        const { user, token } = await loginUser(
          formData.email,
          formData.password
        );
        await verifyToken();
        reconnectSocket();

        if (user) {
          localStorage.setItem(
            "userData",
            JSON.stringify({ username: user.username, image: user.avatar_url })
          );
          if (token) localStorage.setItem("token", token);
          toast.success(`Welcome back, ${user.username}!`);
          onLoginSuccess?.();
        }
      } else {
        if (step === 1) {
          if (formData.password !== formData.confirmPassword) {
            toast.error("Passwords do not match");
            setIsLoading(false);
            return;
          }
          setStep(2);
          setIsLoading(false);
          return;
        }
        await registerUser(
          formData.email,
          formData.password,
          formData.username
        );
        toast.success("Registration complete. Please log in.");
        setIsLogin(true);
        setStep(1);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Error");
    } finally {
      setIsLoading(false);
      if (window.grecaptcha && recaptchaWidgetId.current !== null) {
        window.grecaptcha.reset(recaptchaWidgetId.current);
        setRecaptchaToken("");
      }
    }
  };

  const initializeRecaptcha = () => {
    if (!SITE_KEY || !recaptchaRef.current || !window.grecaptcha) return;
    try {
      if (recaptchaWidgetId.current !== null) {
        window.grecaptcha.reset(recaptchaWidgetId.current);
        return;
      }
      recaptchaWidgetId.current = window.grecaptcha.render(
        recaptchaRef.current,
        {
          sitekey: SITE_KEY,
          theme: "dark",
          callback: (token: string) => setRecaptchaToken(token),
          "expired-callback": () => setRecaptchaToken(""),
        }
      );
    } catch {
      // ignore
    }
  };

  return (
    <>
      <Script
        src={`https://www.google.com/recaptcha/api.js?onload=onRecaptchaLoad&render=explicit`}
        strategy="afterInteractive"
        onLoad={() => {
          window.setTimeout(() => initializeRecaptcha(), 100);
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
            <div className="flex justify-center my-2">
              <div ref={recaptchaRef}></div>
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading
                ? "Processing..."
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
