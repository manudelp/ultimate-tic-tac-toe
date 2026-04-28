import { toast } from "sonner";

// ── Clipboard ──────────────────────────────────────────────
export const toastCodeCopied = () =>
  toast.success("Code copied", {
    description: "Share it with your opponent to join.",
    duration: 2000,
  });

export const toastLinkCopied = () =>
  toast.success("Link copied", {
    description: "Send it to your opponent to join.",
    duration: 2000,
  });

// ── Game actions ───────────────────────────────────────────
export const toastNotYourTurn = () =>
  toast.error("Not your turn", {
    id: "not-your-turn",
    description: "Wait for your opponent to move.",
    duration: 2000,
  });

export const toastCellOccupied = () =>
  toast.error("Cell occupied", {
    id: "cell-occupied",
    description: "Choose an empty cell.",
    duration: 2000,
  });

// ── Lobby ──────────────────────────────────────────────────
export const toastInvalidLobbyCode = () =>
  toast.error("Invalid code", {
    id: "invalid-lobby-code",
    description: "Enter a valid 4-character lobby code.",
    duration: 3000,
  });

// ── Connection ─────────────────────────────────────────────
export const toastOpponentLeft = () =>
  toast.warning("Opponent disconnected", {
    id: "opponent-left",
    description: "Waiting for them to rejoin...",
    duration: Infinity,
  });

export const toastOpponentRejoined = () => {
  toast.dismiss("opponent-left");
  toast.success("Opponent reconnected", {
    description: "The game resumes.",
    duration: 3000,
  });
};

export const toastRejoinFailed = () =>
  toast.error("Could not rejoin", {
    description: "The game may have expired.",
    duration: 4000,
  });

export const toastSocketError = (message: string) =>
  toast.error("Connection error", {
    description: message,
    duration: 4000,
  });
