import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faWhatsapp,
  faXTwitter,
  faReddit,
} from "@fortawesome/free-brands-svg-icons";
import { toast } from "sonner";

const Share: React.FC = () => {
  const shareOnWhatsApp = () => {
    const link = window.location.href;
    const message = `Think you're the ultimate strategist? Prove it! 🕹️ Play Ultimate Tic Tac Toe with me: ${link}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, "_blank");
  };

  const shareOnTwitter = () => {
    const link = window.location.href;
    const text = `Challenge your mind and your friends! 🧠🔥 Play Ultimate Tic Tac Toe:`;
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(
        text
      )}&url=${encodeURIComponent(link)}`,
      "_blank"
    );
  };

  const shareOnReddit = () => {
    const link = window.location.href;
    const title =
      "Can you outsmart the bot or your friends? 🕹️ Play Ultimate Tic Tac Toe now!";
    window.open(
      `https://www.reddit.com/submit?url=${encodeURIComponent(
        link
      )}&title=${encodeURIComponent(title)}`,
      "_blank"
    );
  };
  return (
    <div className="mt-8 text-center">
      <h3 className="mb-2">Share with friends!</h3>
      <div className="flex justify-center gap-6">
        <button
          title="Share on WhatsApp"
          onClick={() => {
            shareOnWhatsApp();
            toast.success("Thank you for sharing on WhatsApp!");
          }}
          className="text-3xl transition-colors hover:text-green-500"
        >
          <FontAwesomeIcon icon={faWhatsapp} />
        </button>
        <button
          title="Share on Twitter"
          onClick={() => {
            shareOnTwitter();
            toast.success("Thank you for sharing on Twitter!");
          }}
          className="text-3xl transition-colors hover:text-black"
        >
          <FontAwesomeIcon icon={faXTwitter} />
        </button>
        <button
          title="Share on Reddit"
          onClick={() => {
            shareOnReddit();
            toast.success("Thank you for sharing on Reddit!");
          }}
          className="text-3xl transition-colors hover:text-orange-600"
        >
          <FontAwesomeIcon icon={faReddit} />
        </button>
      </div>
    </div>
  );
};

export default Share;
