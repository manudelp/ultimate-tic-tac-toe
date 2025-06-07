"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";

export default function Callback() {
  const router = useRouter();

  useEffect(() => {
    const checkSession = async () => {
      const { data, error } = await supabase.auth.getSession();

      if (error || !data.session) {
        toast.error("Login failed");
        router.push("/login");
        return;
      }

      toast.success("Login successful");

      const origin = window.location.origin;
      if (
        origin.includes("utictatoe.online") ||
        origin.includes("utictactoe.vercel.app") ||
        origin.includes("localhost:3000")
      ) {
        router.push("/");
      } else {
        // fallback or other origin
        router.push("/");
      }
    };

    checkSession();
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div>
        <Loader />
        <p className="text-gray-400">Completing login...</p>
      </div>
    </div>
  );
}
