"use client";
import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { LoginForm } from "../ui/login-form";
import {
  supabase,
  getNormalizedUserData,
  validateSession,
} from "@/lib/supabase";
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
import { Session } from "@supabase/supabase-js";

interface UserData {
  name: string;
  username: string;
  image: string;
  provider: string;
  emailVerified: boolean;
}

const Header: React.FC = () => {
  const [showHeader, setShowHeader] = useState(true);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [hostname, setHostname] = useState("utictactoe.online");
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sessionChecked, setSessionChecked] = useState(false);

  const updateUserFromSession = useCallback(async (session: Session | null) => {
    if (session?.user) {
      const userData = getNormalizedUserData(session.user);
      if (userData) {
        const userForState = {
          name: userData.name || userData.username,
          username: userData.username,
          image: userData.avatar_url || "",
          provider: userData.provider,
          emailVerified: userData.emailVerified,
        };

        setUser(userForState);
        localStorage.setItem("userData", JSON.stringify(userData));

        // Sync with backend if needed (for bot games, etc.)
        // This is optional since you mentioned backend isn't handling auth
        const token = localStorage.getItem("token");
        if (!token && userData.provider === "email") {
          // Only try to sync email users with backend
          // Google users don't need backend sync in your current setup
          console.log(
            "Email user logged in, backend sync could be implemented here"
          );
        }
      }
    } else {
      setUser(null);
      localStorage.removeItem("userData");
      localStorage.removeItem("token"); // Clear any backend tokens
    }
  }, []);

  const checkAuthState = useCallback(async () => {
    if (sessionChecked) return; // Prevent multiple checks

    try {
      setIsLoading(true);
      const session = await validateSession();

      if (session) {
        await updateUserFromSession(session);
      } else {
        setUser(null);
        localStorage.removeItem("userData");
        localStorage.removeItem("token");
      }
    } catch (error) {
      console.error("Auth state check failed:", error);
      setUser(null);
      localStorage.removeItem("userData");
      localStorage.removeItem("token");
    } finally {
      setIsLoading(false);
      setSessionChecked(true);
    }
  }, [sessionChecked, updateUserFromSession]);

  useEffect(() => {
    setHostname(window.location.hostname.replace(/^www\./, ""));

    // Initial auth check
    checkAuthState();

    // Subscribe to auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log(
        "Auth state changed:",
        event,
        session?.user?.email,
        session?.user?.app_metadata?.provider
      );

      // Handle different auth events
      switch (event) {
        case "SIGNED_IN":
          await updateUserFromSession(session);
          setIsLoading(false);
          break;

        case "SIGNED_OUT":
          setUser(null);
          localStorage.removeItem("userData");
          localStorage.removeItem("token");
          setIsLoading(false);
          break;

        case "TOKEN_REFRESHED":
          // Session was refreshed, update user data
          if (session) {
            await updateUserFromSession(session);
          }
          break;

        case "USER_UPDATED":
          // User profile was updated
          if (session) {
            await updateUserFromSession(session);
          }
          break;

        default:
          console.log("Unhandled auth event:", event);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [checkAuthState, updateUserFromSession]);

  const handleLogout = async () => {
    try {
      setIsLoading(true);

      // Sign out from Supabase
      const { error } = await supabase.auth.signOut();

      if (error) {
        console.error("Logout error:", error);
        toast.error("Logout failed");
        return;
      }

      // Clear all local state and storage
      setUser(null);
      setShowLoginModal(false);
      setShowMobileMenu(false);
      localStorage.removeItem("userData");
      localStorage.removeItem("token");

      toast.success("Logged out successfully");
    } catch (error) {
      console.error("Logout error:", error);
      toast.error("Logout failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = () => {
    setShowLoginModal(false);
    // Auth state change will be handled by the subscription
  };

  // Show provider-specific user info
  const getUserDisplayInfo = () => {
    if (!user) return null;

    return {
      ...user,
      displayName: user.name || user.username,
      providerBadge:
        user.provider === "google"
          ? "🔗 Google"
          : user.emailVerified
          ? "✅ Email"
          : "⚠️ Unverified",
    };
  };

  useEffect(() => {
    let lastScrollTop = 0;
    let scrollTimer: NodeJS.Timeout | null = null;
    let hideTimer: NodeJS.Timeout | null = null;

    const handleScroll = () => {
      const currentScrollTop =
        window.pageYOffset || document.documentElement.scrollTop;

      if (scrollTimer) clearTimeout(scrollTimer);
      if (hideTimer) clearTimeout(hideTimer);

      if (showMobileMenu || showLoginModal) {
        if (!showHeader) {
          setShowHeader(true);
        }
        lastScrollTop = currentScrollTop;
        return;
      }

      if (currentScrollTop <= 50) {
        if (!showHeader) {
          setShowHeader(true);
        }
        lastScrollTop = currentScrollTop;
        return;
      }

      const scrollDifference = Math.abs(currentScrollTop - lastScrollTop);
      if (scrollDifference < 5) return;

      scrollTimer = setTimeout(() => {
        if (currentScrollTop > lastScrollTop && showHeader) {
          hideTimer = setTimeout(() => {
            setShowHeader(false);
          }, 150);
        } else if (currentScrollTop < lastScrollTop && !showHeader) {
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

  const userInfo = getUserDisplayInfo();

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-20 transition ${
        !showHeader ? "-translate-y-full" : ""
      } ${showMobileMenu ? "bg-gray-900" : ""}`}
    >
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center">
          <Link
            href="/"
            className="text-xl font-bold truncate max-w-[200px] sm:max-w-none"
          >
            {hostname}
          </Link>
        </div>

        <nav className="hidden md:block">
          <ul className="flex items-center space-x-6">
            <li>
              <Link
                href="/"
                className="relative transition-colors hover:text-white after:absolute after:bottom-[-6px] after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all hover:after:w-full"
              >
                Home
              </Link>
            </li>
            <li>
              <Link
                href="/how-to-play"
                className="relative transition-colors hover:text-white after:absolute after:bottom-[-6px] after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all hover:after:w-full"
              >
                How to Play
              </Link>
            </li>
            <li>
              {isLoading ? (
                <div className="w-20 h-8 bg-gray-600 rounded-md animate-pulse"></div>
              ) : userInfo ? (
                <div className="flex items-center gap-2">
                  <DropdownMenu modal={false}>
                    <DropdownMenuTrigger asChild>
                      <Avatar className="cursor-pointer hover:ring-2 hover:ring-gray-500 transition">
                        <AvatarImage
                          src={userInfo.image}
                          alt={userInfo.displayName}
                        />
                        <AvatarFallback>
                          {userInfo.displayName.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-64">
                      <DropdownMenuLabel className="text-sm font-semibold">
                        <div className="flex flex-col">
                          <span
                            className="truncate"
                            title={userInfo.displayName}
                          >
                            {userInfo.displayName}
                          </span>
                          <span className="text-xs text-gray-500 font-normal">
                            {userInfo.providerBadge}
                          </span>
                        </div>
                      </DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <Link href="/profile" title="Profile">
                        <DropdownMenuItem>Profile</DropdownMenuItem>
                      </Link>
                      <DropdownMenuItem
                        onClick={handleLogout}
                        className="text-red-500"
                        disabled={isLoading}
                      >
                        {isLoading ? "Logging out..." : "Logout"}
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
                    <Link
                      href="/profile"
                      className="w-2/3 flex items-center gap-2"
                      onClick={() => setShowMobileMenu(false)}
                    >
                      <Avatar>
                        <AvatarImage
                          src={user.image}
                          alt={user.name || user.username}
                        />
                        <AvatarFallback>
                          {(user.name || user.username).charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <span
                        className="text-white w-full truncate"
                        title={user.name || user.username}
                      >
                        {user.name || user.username}
                      </span>
                    </Link>
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
