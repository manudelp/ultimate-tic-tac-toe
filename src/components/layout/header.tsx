"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { LoginForm } from "../ui/login-form";
import { logoutUser, verifyToken } from "@/api";
import { Button } from "../ui/button";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Header: React.FC = () => {
  const [showHeader, setShowHeader] = useState(true);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [hostname, setHostname] = useState("utictactoe.online");
  const [user, setUser] = useState<{ name: string; image: string } | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token and verify it
  const checkAuth = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (token) {
        const isValid = await verifyToken();
        if (isValid) {
          const userData = localStorage.getItem("userData");
          if (userData) {
            const parsedUserData = JSON.parse(userData);
            setUser({ name: parsedUserData.name, image: parsedUserData.image });
          }
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

  useEffect(() => {
    setHostname(window.location.hostname.replace(/^www\./, ""));
    checkAuth();
  }, []);

  const handleLogout = () => {
    logoutUser();
    setUser(null);
    toast.success("You've been logged out successfully");
  };

  const handleLoginSuccess = () => {
    setShowLoginModal(false);
    checkAuth();
  };

  useEffect(() => {
    let lastScrollTop = 0;
    let scrollTimer: NodeJS.Timeout | null = null;
    let hideTimer: NodeJS.Timeout | null = null;

    const handleScroll = () => {
      const currentScrollTop =
        window.pageYOffset || document.documentElement.scrollTop;

      // Clear existing timers
      if (scrollTimer) clearTimeout(scrollTimer);
      if (hideTimer) clearTimeout(hideTimer);

      // Don't hide header if mobile menu or login modal is open
      if (showMobileMenu || showLoginModal) {
        if (!showHeader) {
          setShowHeader(true);
        }
        lastScrollTop = currentScrollTop;
        return;
      }

      // Always show header when near top
      if (currentScrollTop <= 50) {
        if (!showHeader) {
          setShowHeader(true);
        }
        lastScrollTop = currentScrollTop;
        return;
      }

      const scrollDifference = Math.abs(currentScrollTop - lastScrollTop);

      // Only react to significant 5px scroll changes
      if (scrollDifference < 5) {
        return;
      }

      // Add delay before hiding/showing to prevent flickering
      scrollTimer = setTimeout(() => {
        if (currentScrollTop > lastScrollTop && showHeader) {
          // Scrolling down - hide after a small delay
          hideTimer = setTimeout(() => {
            setShowHeader(false);
          }, 150);
        } else if (currentScrollTop < lastScrollTop && !showHeader) {
          // Scrolling up - show immediately for better UX
          setShowHeader(true);
        }

        lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop;
      }, 50);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (scrollTimer) clearTimeout(scrollTimer);
      if (hideTimer) clearTimeout(hideTimer);
    };
  }, [showHeader, showLoginModal, showMobileMenu]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-20 transition ${
        !showHeader ? "-translate-y-full" : ""
      } ${showMobileMenu ? "bg-gray-900" : ""}`}
    >
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Left side - Logo/Hostname */}
        <div className="flex items-center">
          <Link
            href="/"
            className="text-xl font-bold truncate max-w-[200px] sm:max-w-none"
          >
            {hostname}
          </Link>
        </div>

        {/* Right side - Desktop Navigation */}
        <nav className="hidden md:block">
          <ul className="flex items-center space-x-6">
            <li>
              <Link
                href="/"
                className="transition-colors hover:text-gray-300 hover:underline"
              >
                Home
              </Link>
            </li>
            <li>
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
                <div className="flex items-center gap-2">
                  <DropdownMenu modal={false}>
                    <DropdownMenuTrigger asChild>
                      <Avatar className="cursor-pointer hover:ring-2 hover:ring-gray-500 transition">
                        <AvatarImage src={user.image} alt={user.name} />
                        <AvatarFallback>
                          {user.name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>
                        <div className="max-w-[200px] truncate">
                          {user.name}
                        </div>
                      </DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={handleLogout}
                        className="text-red-500"
                      >
                        Logout
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ) : (
                <Button onClick={() => setShowLoginModal(true)}>Login</Button>
              )}
            </li>
          </ul>
        </nav>

        {/* Mobile hamburger button */}
        <button
          className="block md:hidden p-2 flex-shrink-0"
          onClick={() => setShowMobileMenu(!showMobileMenu)}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            {showMobileMenu ? (
              <>
                <motion.line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                  initial={{ opacity: 0, pathLength: 0 }}
                  animate={{ opacity: 1, pathLength: 1 }}
                  transition={{ duration: 0.3 }}
                ></motion.line>
                <motion.line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                  initial={{ opacity: 0, pathLength: 0 }}
                  animate={{ opacity: 1, pathLength: 1 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                ></motion.line>
              </>
            ) : (
              <>
                <motion.line
                  x1="3"
                  y1="12"
                  x2="21"
                  y2="12"
                  initial={{ opacity: 0, pathLength: 0 }}
                  animate={{ opacity: 1, pathLength: 1 }}
                  transition={{ duration: 0.3 }}
                ></motion.line>
                <motion.line
                  x1="3"
                  y1="6"
                  x2="21"
                  y2="6"
                  initial={{ opacity: 0, pathLength: 0 }}
                  animate={{ opacity: 1, pathLength: 1 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                ></motion.line>
                <motion.line
                  x1="3"
                  y1="18"
                  x2="21"
                  y2="18"
                  initial={{ opacity: 0, pathLength: 0 }}
                  animate={{ opacity: 1, pathLength: 1 }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                ></motion.line>
              </>
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Navigation Menu with Animation */}
      <AnimatePresence>
        {showMobileMenu && (
          <motion.div
            className="absolute top-full left-0 right-0 bg-background border-t border-gray-700 md:hidden"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ul className="flex flex-col">
              <motion.li
                className="p-3 border-b border-gray-700 bg-gray-900"
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                <Link
                  href="/"
                  className="block transition-colors hover:text-gray-300"
                  onClick={() => setShowMobileMenu(false)}
                >
                  Home
                </Link>
              </motion.li>
              <motion.li
                className="p-3 border-b border-gray-700 bg-gray-900"
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Link
                  href="/how-to-play"
                  className="block transition-colors hover:text-gray-300"
                  onClick={() => setShowMobileMenu(false)}
                >
                  How to Play
                </Link>
              </motion.li>
              <motion.li
                className="p-3 border-b border-gray-700 bg-gray-900"
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                {isLoading ? (
                  <div className="w-20 h-8 bg-gray-600 rounded-md animate-pulse"></div>
                ) : user ? (
                  <div className="flex justify-between gap-2">
                    <div className="w-2/3 flex items-center gap-2">
                      <Avatar>
                        <AvatarImage src={user.image} alt={user.name} />
                        <AvatarFallback>
                          {user.name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <span
                        className="text-white w-full truncate"
                        title={user.name}
                      >
                        {user.name}
                      </span>
                    </div>
                    <Button
                      onClick={() => {
                        handleLogout();
                        setShowMobileMenu(false);
                      }}
                      className="px-4 py-2 text-white transition-colors bg-red-600 rounded-md hover:bg-red-700"
                    >
                      Logout
                    </Button>
                  </div>
                ) : (
                  <Button
                    onClick={() => {
                      setShowMobileMenu(false);
                      setShowLoginModal(true);
                    }}
                    className="w-full px-4 py-2 text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    Login
                  </Button>
                )}
              </motion.li>
            </ul>
          </motion.div>
        )}
      </AnimatePresence>

      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="fixed inset-0 bg-black/50 cursor-pointer"
            onClick={() => setShowLoginModal(false)}
          ></div>
          <div className="relative">
            <button
              onClick={() => setShowLoginModal(false)}
              className="absolute flex items-center justify-center w-8 h-8 text-white bg-gray-700 rounded-full top-2 right-2 transition hover:bg-red-600 active:scale-90"
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
