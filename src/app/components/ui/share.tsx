import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faWhatsapp,
  faXTwitter,
  faReddit,
} from "@fortawesome/free-brands-svg-icons";
import { toast } from "react-toastify";

const Share: React.FC = () => {
  const shareOnWhatsApp = () => {
    // Logic for sharing on WhatsApp
  };

  const shareOnTwitter = () => {
    // Logic for sharing on Twitter
  };

  const shareOnReddit = () => {
    // Logic for sharing on Reddit
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
