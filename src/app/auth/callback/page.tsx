"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";
import Loader from "@/components/ui/loader";

export default function Callback() {
  const router = useRouter();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Get the session from Supabase
        const { data, error } = await supabase.auth.getSession();

        if (error || !data.session) {
          toast.error("Login failed");
          router.push("/");
          return;
        }

        // Store user data in localStorage for UI state management
        const userData = {
          id: data.session.user.id,
          email: data.session.user.email,
          name:
            data.session.user.user_metadata?.full_name ||
            data.session.user.user_metadata?.name ||
            data.session.user.email?.split("@")[0],
          username:
            data.session.user.user_metadata?.user_name ||
            data.session.user.email?.split("@")[0],
          avatar_url: data.session.user.user_metadata?.avatar_url,
        };

        localStorage.setItem("userData", JSON.stringify(userData));

        toast.success("Login successful");
        router.push("/");
      } catch (error) {
        console.error("Auth callback error:", error);
        toast.error("Login failed");
        router.push("/");
      }
    };

    handleAuthCallback();
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
