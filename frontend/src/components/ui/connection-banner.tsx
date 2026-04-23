"use client";
import { useConnection } from "@/hooks/useConnection";

export default function ConnectionBanner() {
  const { connected, checking } = useConnection();

  if (checking || connected) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-red-900/90 backdrop-blur-sm text-white text-center py-2 px-4 text-sm">
      Server is unreachable — some features may not work.
    </div>
  );
}
