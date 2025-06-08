"use client";
import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { LoginForm } from "../ui/login-form";
import {
  supabase,
  validateSession,
  getUserProfileWithLinking,
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
import { toUIUserData } from "@/lib/supabase";

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

  // Ensure we're on the client side
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Enhanced user profile loading with proper error handling - provider-agnostic
  const loadUserProfile = useCallback(
    async (session: SupabaseSession): Promise<UIUserData | null> => {
      if (!session?.user || typeof window === "undefined") {
        return null;
      }

      try {
        console.log("Loading user profile for:", {
          userId: session.user.id,
          email: session.user.email,
        });

        const userData = await getUserProfileWithLinking(session.user);

        if (!userData) {
          console.error("Failed to load user profile data");
          return null;
        }

        console.log("Successfully loaded profile:", {
          userId: userData.id,
          username: userData.username,
          name: userData.name,
        });

        // Convert to provider-agnostic UI data
        return toUIUserData(userData);
      } catch (error) {
        console.error("Error loading user profile:", error);
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
          console.log("Updating user from session:", {
            userId: session.user.id,
            email: session.user.email,
          });

          const userForState = await loadUserProfile(session);

          if (userForState) {
            setAuthState((prev) => ({
              ...prev,
              user: userForState,
              error: null,
            }));

            const userData = await getUserProfileWithLinking(session.user);
            if (userData) {
              localStorage.setItem("userData", JSON.stringify(userData));
            }

            console.log("User state updated successfully:", userForState);
          } else {
            console.error("Failed to load user profile data");
            setAuthState((prev) => ({
              ...prev,
              error: "Failed to load user profile",
            }));
          }
        } else {
          console.log("No session user, clearing user state");
          setAuthState((prev) => ({
            ...prev,
            user: null,
            error: null,
          }));
          localStorage.removeItem("userData");
          localStorage.removeItem("token");
        }
      } catch (error) {
        console.error("Error updating user from session:", error);
        setAuthState((prev) => ({
          ...prev,
          user: null,
          error: error instanceof Error ? error.message : "Unknown error",
        }));
        localStorage.removeItem("userData");
        localStorage.removeItem("token");
      }
    },
    [loadUserProfile]
  );

  const checkAuthState = useCallback(async (): Promise<void> => {
    if (authState.sessionChecked || typeof window === "undefined") return;

    try {
      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));
      console.log("Checking initial auth state...");

      const sessionResult = await validateSession();
      console.log(
        "Initial session check result:",
        sessionResult.isValid ? "Session found" : "No session"
      );

      if (sessionResult.error) {
        setAuthState((prev) => ({
          ...prev,
          error: sessionResult.error || "Session validation failed",
        }));
      }

      await updateUserFromSession(sessionResult.session);
    } catch (error) {
      console.error("Auth state check failed:", error);
      setAuthState((prev) => ({
        ...prev,
        user: null,
        error: error instanceof Error ? error.message : "Auth check failed",
      }));
      localStorage.removeItem("userData");
      localStorage.removeItem("token");
    } finally {
      setAuthState((prev) => ({
        ...prev,
        isLoading: false,
        sessionChecked: true,
      }));
    }
  }, [authState.sessionChecked, updateUserFromSession]);

  useEffect(() => {
    if (!isClient) return;

    setHostname(window.location.hostname.replace(/^www\./, ""));

    // Initial auth check
    checkAuthState();

    // Subscribe to auth state changes with enhanced logging
    if (!supabase.auth) return;

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log("Auth state change detected:", {
        event,
        userId: session?.user?.id,
        email: session?.user?.email,
        hasSession: !!session,
      });

      // Reset session checked flag on auth events to allow re-checking
      if (event === "SIGNED_IN" || event === "SIGNED_OUT") {
        setAuthState((prev) => ({ ...prev, sessionChecked: false }));
      }

      // Handle different auth events with proper state management
      switch (event) {
        case "SIGNED_IN":
          console.log("Processing SIGNED_IN event");
          setAuthState((prev) => ({ ...prev, isLoading: true }));
          await updateUserFromSession(session);
          setAuthState((prev) => ({ ...prev, isLoading: false }));
          break;

        case "SIGNED_OUT":
          console.log("Processing SIGNED_OUT event");
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
          console.log(`Processing ${event} event`);
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
  }, [checkAuthState, updateUserFromSession, isClient]);

  // Enhanced logout with proper cleanup and error handling
  const handleLogout = async (): Promise<void> => {
    try {
      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));
      console.log("Initiating logout...");

      if (!supabase.auth) {
        throw new Error("Supabase auth not available");
      }

      // Sign out from Supabase
      const { error } = await supabase.auth.signOut();

      if (error) {
        console.error("Logout error:", error);
        toast.error("Logout failed");
        return;
      }

      // Clear all local state and storage
      setAuthState({
        user: null,
        isLoading: false,
        sessionChecked: false,
        error: null,
      });
      setShowLoginModal(false);
      setShowMobileMenu(false);
      localStorage.removeItem("userData");
      localStorage.removeItem("token");

      console.log("Logout completed successfully");
      toast.success("Logged out successfully");
    } catch (error) {
      console.error("Logout error:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Logout failed";
      setAuthState((prev) => ({ ...prev, error: errorMessage }));
      toast.error(errorMessage);
    } finally {
      setAuthState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  const handleLoginSuccess = (): void => {
    console.log("Login success callback triggered");
    setShowLoginModal(false);
    // Force a session check to ensure immediate UI update
    setTimeout(() => {
      checkAuthState();
    }, 100);
  };

  // Show provider-agnostic user info
  const getUserDisplayInfo = () => {
    if (!authState.user) return null;

    return {
      ...authState.user,
      displayName: authState.user.name || authState.user.username,
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

  // Enhanced debug logging for development - no provider exposure
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("Header state:", {
        isLoading: authState.isLoading,
        sessionChecked: authState.sessionChecked,
        hasUser: !!authState.user,
        username: authState.user?.username,
        error: authState.error,
      });
    }
  }, [authState]);

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
