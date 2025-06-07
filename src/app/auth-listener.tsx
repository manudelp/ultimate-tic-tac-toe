"use client";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export default function AuthListener() {
  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      // Session updated
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  return null;
}
