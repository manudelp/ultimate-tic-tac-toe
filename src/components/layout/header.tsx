"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { LoginForm } from "../ui/login-form";
import { getCurrentUser, logoutUser, verifyToken } from "@/api";
import { Button } from "../ui/button";
import { toast } from "sonner";

const Header: React.FC = () => {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [hostname, setHostname] = useState("utictactoe.online");
  const [user, setUser] = useState<{ name: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setHostname(window.location.hostname);

    // Check for existing token and verify it
    const checkAuth = async () => {
      setIsLoading(true);
      try {
        const token = localStorage.getItem("token");
        if (token) {
          const result = await verifyToken();
          if (result.valid && result.data) {
            setUser({ name: result.data.name });
          } else {
            // Invalid token, clear it
            localStorage.removeItem("token");
            localStorage.removeItem("userData");
          }
        }
      } catch (error) {
        console.error("Authentication error:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = () => {
    logoutUser();
    setUser(null);
    toast.success("You've been logged out successfully");
  };

  const handleLoginSuccess = () => {
    setShowLoginModal(false);
    const userData = getCurrentUser();
    if (userData) {
      setUser({ name: userData.name });
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-4 bg-background">
      <div className="container flex items-center justify-between mx-auto">
        <Link href="/" className="text-xl font-bold">
          {hostname}
        </Link>
        <nav>
          <ul className="flex items-center space-x-6">
            <li className="p-2">
              <Link
                href="/"
                className="transition-colors hover:text-gray-300 hover:underline"
              >
                Home
              </Link>
            </li>
            <li className="p-2">
              <Link
                href="/how-to-play"
                className="transition-colors hover:text-gray-300 hover:underline"
              >
                How to Play
              </Link>
            </li>
            <li>
              {isLoading ? (
                <div className="w-20 h-8 bg-gray-600 rounded-md animate-pulse"></div>
              ) : user ? (
                <div className="flex items-center gap-4">
                  <span className="text-white">Welcome, {user.name}!</span>
                  <Button
                    onClick={handleLogout}
                    className="px-4 py-2 text-white transition-colors bg-red-600 rounded-md hover:bg-red-700"
                  >
                    Logout
                  </Button>
                </div>
              ) : (
                <Button
                  onClick={() =>
                    toast.info("We are working on the login feature!")
                  }
                  className="px-4 py-2 text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  Login
                </Button>
              )}
            </li>
          </ul>
        </nav>
      </div>

      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="relative max-w-md">
            <button
              onClick={() => setShowLoginModal(false)}
              className="absolute flex items-center justify-center w-8 h-8 text-white bg-gray-700 rounded-full top-2 right-2 hover:bg-gray-600"
            >
              ✕
            </button>
            <LoginForm onLoginSuccess={handleLoginSuccess} />
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;
