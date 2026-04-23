import { useState, useEffect } from "react";
import { checkConnection } from "@/api";

export function useConnection() {
  const [connected, setConnected] = useState(true);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let mounted = true;

    const check = async () => {
      const ok = await checkConnection();
      if (mounted) {
        setConnected(ok);
        setChecking(false);
      }
    };

    check();

    const interval = setInterval(check, 30000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  return { connected, checking };
}
