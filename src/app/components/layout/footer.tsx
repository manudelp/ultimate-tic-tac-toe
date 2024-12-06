"use client";
import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

interface FooterProps {
  isBackendConnected: boolean;
}

const Footer: React.FC<FooterProps> = ({ isBackendConnected }) => {
  useEffect(() => {
    const year = new Date().getFullYear();
    if (typeof window !== "undefined") {
      const yearElement = document.getElementById("year");
      if (yearElement) {
        yearElement.innerHTML = year.toString();
      }
    }
  }, []);

  return (
    <div className="w-full min-h-fit flex flex-col items-center justify-center gap-2  p-8 text-sm text-white text-center bg-gray-950">
      <div>
        <p>
          &copy; <span id="year"></span> Ultimate Tic Tac Toe. All rights
          reserved.
        </p>
        <p>
          Developed by{" "}
          <a
            href="https://www.linkedin.com/in/manuel-delpino/"
            target="_blank"
            className="text-blue-400 hover:underline"
            rel="noopener noreferrer"
          >
            Manuel Delpino
          </a>{" "}
          &{" "}
          <a
            href="https://www.linkedin.com/in/manuel-meiriño-7b9214331/"
            target="_blank"
            className="text-blue-400 hover:underline"
            rel="noopener noreferrer"
          >
            Manuel Meiriño
          </a>
        </p>
      </div>
      <div>
        <Link to="/privacy-policy" className="text-blue-400 hover:underline">
          <button>Privacy Policy</button>
        </Link>{" "}
        |{" "}
        <Link to="/terms-of-service" className="text-blue-400 hover:underline">
          <button>Terms of Service</button>
        </Link>{" "}
        |{" "}
        <Link to="/contact" className="text-blue-400 hover:underline">
          <button className="cursor-not-allowed" disabled>
            Contact Us
          </button>
        </Link>{" "}
        |{" "}
        <Link to="/how-to-play" className="text-blue-400 hover:underline">
          <button>How to Play</button>
        </Link>
      </div>
      <div>
        <p>
          Stay connected with us on{" "}
          <a
            href="#"
            className="text-blue-400 hover:underline"
            rel="noopener noreferrer"
            onClick={() => toast.info("We dont have an Instagram account yet!")}
          >
            Instagram
          </a>
          .
        </p>
      </div>
      <div>
        {isBackendConnected ? (
          <p>🟢 Server is operational.</p>
        ) : (
          <p>🛑 Server is offline.</p>
        )}
      </div>
    </div>
  );
};

export default Footer;
