"use client";
import React, { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { LoginForm } from "../ui/login-form";
import {
  supabase,
  validateSession,
  getUserProfileWithLinking,
  toUIUserData,
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
import { Session as SupabaseSession } from "@supabase/supabase-js";
import { UIUserData, AuthState } from "@/types/auth";

// Custom event interface for auth state changes
interface AuthStateChangeDetail {
  event: string;
  session: SupabaseSession | null;
}

interface AuthStateChangeEvent extends Event {
  detail: AuthStateChangeDetail;
}

const Header: React.FC = () => {
  const [showHeader, setShowHeader] = useState(true);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [hostname, setHostname] = useState("utictactoe.online");
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isLoading: true,
    sessionChecked: false,
    error: null,
  });
  const [isClient, setIsClient] = useState(false);
  const authTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const sessionCheckRef = useRef<boolean>(false);

  // Ensure we're on the client side
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Detect client clock skew that could prevent session validation
  const checkClockSkew = useCallback(() => {
    try {
      const now = Date.now();
      const stored = localStorage.getItem("last_auth_check");
      if (stored) {
        const lastCheck = parseInt(stored);
        const diff = Math.abs(now - lastCheck);
        // If more than 24 hours difference, warn about potential clock skew
        if (diff > 24 * 60 * 60 * 1000) {
          setAuthState((prev) => ({
            ...prev,
            error:
              "System clock may be incorrect. Please check your device time.",
          }));
        }
      }
      localStorage.setItem("last_auth_check", now.toString());
    } catch {
      // Silent handling of clock skew check errors
    }
  }, []);

  // Reset auth state to handle persistent loading issues
  const resetAuthState = useCallback(() => {
    setAuthState({
      user: null,
      isLoading: false,
      sessionChecked: true,
      error: null,
    });
    localStorage.removeItem("userData");
    localStorage.removeItem("token");
  }, []);

  // Enhanced user profile loading with timeout protection
  const loadUserProfile = useCallback(
    async (session: SupabaseSession): Promise<UIUserData | null> => {
      if (!session?.user || typeof window === "undefined") {
        return null;
      }

      try {
        // Set a timeout for profile loading
        const timeoutPromise = new Promise<null>((_, reject) => {
          setTimeout(() => reject(new Error("Profile load timeout")), 5000);
        });

        const profilePromise = getUserProfileWithLinking(session.user);

        const userData = await Promise.race([profilePromise, timeoutPromise]);

        if (!userData) {
          return null;
        }

        return toUIUserData(userData);
      } catch {
        return null;
      }
    },
    []
  );

  const updateUserFromSession = useCallback(
    async (session: SupabaseSession | null): Promise<void> => {
      if (typeof window === "undefined") return;

      try {
        if (session?.user) {
          const userForState = await loadUserProfile(session);

          if (userForState) {
            setAuthState((prev) => ({
              ...prev,
              user: userForState,
              error: null,
              isLoading: false,
              sessionChecked: true,
            }));

            const userData = await getUserProfileWithLinking(session.user);
            if (userData) {
              localStorage.setItem("userData", JSON.stringify(userData));
            }
          } else {
            setAuthState((prev) => ({
              ...prev,
              user: null,
              error: "Failed to load user profile",
              isLoading: false,
              sessionChecked: true,
            }));
          }
        } else {
          setAuthState((prev) => ({
            ...prev,
            user: null,
            error: null,
            isLoading: false,
            sessionChecked: true,
          }));
          localStorage.removeItem("userData");
          localStorage.removeItem("token");
        }
      } catch (err) {
        setAuthState((prev) => ({
          ...prev,
          user: null,
          error: err instanceof Error ? err.message : "Unknown error",
          isLoading: false,
          sessionChecked: true,
        }));
        localStorage.removeItem("userData");
        localStorage.removeItem("token");
      }
    },
    [loadUserProfile]
  );

  const checkAuthState = useCallback(async (): Promise<void> => {
    if (sessionCheckRef.current || typeof window === "undefined") return;

    sessionCheckRef.current = true;

    try {
      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));

      checkClockSkew();

      // Set timeout for session validation
      const timeoutPromise = new Promise<never>((_, reject) => {
        authTimeoutRef.current = setTimeout(() => {
          reject(new Error("Session validation timeout"));
        }, 8000);
      });

      const sessionPromise = validateSession();

      const sessionResult = await Promise.race([
        sessionPromise,
        timeoutPromise,
      ]);

      if (authTimeoutRef.current) {
        clearTimeout(authTimeoutRef.current);
        authTimeoutRef.current = null;
      }

      if (sessionResult.error) {
        setAuthState((prev) => ({
          ...prev,
          error: sessionResult.error || "Session validation failed",
          isLoading: false,
          sessionChecked: true,
        }));
        return;
      }

      await updateUserFromSession(sessionResult.session);
    } catch (err) {
      if (authTimeoutRef.current) {
        clearTimeout(authTimeoutRef.current);
        authTimeoutRef.current = null;
      }

      setAuthState((prev) => ({
        ...prev,
        user: null,
        error: err instanceof Error ? err.message : "Auth check failed",
        isLoading: false,
        sessionChecked: true,
      }));
      localStorage.removeItem("userData");
      localStorage.removeItem("token");
    } finally {
      sessionCheckRef.current = false;
    }
  }, [updateUserFromSession, checkClockSkew]);

  // Handle auth state changes from AuthListener
  useEffect(() => {
    if (!isClient) return;

    const handleAuthStateChange = async (event: Event) => {
      const customEvent = event as AuthStateChangeEvent;
      const { event: authEvent, session } = customEvent.detail;

      // Reset session check flag to allow new checks
      sessionCheckRef.current = false;

      switch (authEvent) {
        case "INITIAL_SESSION":
        case "SIGNED_IN":
          setAuthState((prev) => ({ ...prev, isLoading: true }));
          await updateUserFromSession(session);
          break;

        case "SIGNED_OUT":
          setAuthState({
            user: null,
            isLoading: false,
            sessionChecked: true,
            error: null,
          });
          localStorage.removeItem("userData");
          localStorage.removeItem("token");
          break;

        case "TOKEN_REFRESHED":
        case "USER_UPDATED":
          if (session) {
            await updateUserFromSession(session);
          }
          break;

        default:
          // Handle unknown events by resetting loading state
          setAuthState((prev) => ({
            ...prev,
            isLoading: false,
            sessionChecked: true,
          }));
          break;
      }
    };

    const handleAuthTimeout = () => {
      resetAuthState();
    };

    // Listen for auth events from AuthListener
    window.addEventListener("auth-state-change", handleAuthStateChange);
    window.addEventListener("auth-timeout", handleAuthTimeout);

    // Initial setup
    setHostname(window.location.hostname.replace(/^www\./, ""));

    // Initial auth check with fallback timeout
    const initialTimeout = setTimeout(() => {
      if (!authState.sessionChecked) {
        resetAuthState();
      }
    }, 12000); // 12 second fallback

    checkAuthState().finally(() => {
      clearTimeout(initialTimeout);
    });

    return () => {
      window.removeEventListener("auth-state-change", handleAuthStateChange);
      window.removeEventListener("auth-timeout", handleAuthTimeout);
      clearTimeout(initialTimeout);
      if (authTimeoutRef.current) {
        clearTimeout(authTimeoutRef.current);
      }
    };
  }, [
    isClient,
    checkAuthState,
    updateUserFromSession,
    resetAuthState,
    authState.sessionChecked,
  ]);

  // Enhanced logout with proper cleanup and error handling
  const handleLogout = async (): Promise<void> => {
    try {
      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));

      if (!supabase.auth) {
        throw new Error("Supabase auth not available");
      }

      // Set logout timeout
      const logoutTimeout = setTimeout(() => {
        resetAuthState();
        toast.error("Logout timed out but you've been signed out locally");
      }, 5000);

      const { error } = await supabase.auth.signOut();
      clearTimeout(logoutTimeout);

      if (error) {
        toast.error("Logout failed");
        setAuthState((prev) => ({ ...prev, isLoading: false }));
        return;
      }

      resetAuthState();
      setShowLoginModal(false);
      setShowMobileMenu(false);
      toast.success("Logged out successfully");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Logout failed";
      setAuthState((prev) => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
      }));
      toast.error(errorMessage);
    }
  };

  const handleLoginSuccess = (): void => {
    setShowLoginModal(false);
    sessionCheckRef.current = false;
    // Force a session check with short delay
    setTimeout(() => {
      checkAuthState();
    }, 250);
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

  // Don't render until client-side hydration is complete
  if (!isClient) {
    return (
      <header className="fixed top-0 left-0 right-0 z-20 bg-gray-900">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-xl font-bold">utictactoe.online</span>
          </div>
          <nav className="hidden md:block">
            <ul className="flex items-center space-x-6">
              <li>
                <span>Home</span>
              </li>
              <li>
                <span>How to Play</span>
              </li>
              <li>
                <div className="w-20 h-8 bg-gray-600 rounded-md animate-pulse"></div>
              </li>
            </ul>
          </nav>
          <div className="block md:hidden p-2">
            <div className="w-6 h-6 bg-gray-600 rounded"></div>
          </div>
        </div>
      </header>
    );
  }

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
              {authState.isLoading ? (
                <div className="w-20 h-8 bg-gray-600 rounded-md animate-pulse"></div>
              ) : authState.user ? (
                <div className="flex items-center gap-2">
                  <DropdownMenu modal={false}>
                    <DropdownMenuTrigger asChild>
                      <Avatar className="cursor-pointer hover:ring-2 hover:ring-gray-500 transition">
                        <AvatarImage
                          src={authState.user.image}
                          alt={authState.user.name || authState.user.username}
                        />
                        <AvatarFallback>
                          {(authState.user.name || authState.user.username)
                            .charAt(0)
                            .toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-64">
                      <DropdownMenuLabel className="text-sm font-semibold">
                        <div className="flex flex-col">
                          <span
                            className="truncate"
                            title={
                              authState.user.name || authState.user.username
                            }
                          >
                            {authState.user.name || authState.user.username}
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
                        disabled={authState.isLoading}
                      >
                        {authState.isLoading ? "Logging out..." : "Logout"}
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
                {authState.isLoading ? (
                  <div className="w-20 h-8 bg-gray-600 rounded-md animate-pulse"></div>
                ) : authState.user ? (
                  <div className="flex justify-between gap-2">
                    <Link
                      href="/profile"
                      className="w-2/3 flex items-center gap-2"
                      onClick={() => setShowMobileMenu(false)}
                    >
                      <Avatar>
                        <AvatarImage
                          src={authState.user.image}
                          alt={authState.user.name || authState.user.username}
                        />
                        <AvatarFallback>
                          {(authState.user.name || authState.user.username)
                            .charAt(0)
                            .toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <span
                        className="text-white w-full truncate"
                        title={authState.user.name || authState.user.username}
                      >
                        {authState.user.name || authState.user.username}
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
