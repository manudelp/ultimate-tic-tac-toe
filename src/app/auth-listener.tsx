"use client";
import { useEffect, useRef } from "react";
import { supabase } from "@/lib/supabase";

export default function AuthListener() {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Clear any existing timeouts
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (debounceRef.current) clearTimeout(debounceRef.current);

    // Set a fallback timeout to reset loading state if auth check takes too long
    timeoutRef.current = setTimeout(() => {
      // Force reset of any persistent loading states
      window.dispatchEvent(new CustomEvent("auth-timeout"));
    }, 10000); // 10 second timeout

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      // Clear the timeout since we got an auth event
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      // Debounce rapid auth state changes
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      debounceRef.current = setTimeout(() => {
        // Dispatch custom event for components to handle
        window.dispatchEvent(
          new CustomEvent("auth-state-change", {
            detail: { event, session },
          })
        );
      }, 100);
    });

    return () => {
      subscription.unsubscribe();
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  return null;
}
