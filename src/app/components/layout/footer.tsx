"use client";
import React, { useEffect } from "react";
import { Link } from "react-router-dom";

const Footer: React.FC = () => {
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
    <div className="w-full p-8 text-sm text-white text-center bg-gray-950">
      <div className="mb-4">
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
      <div className="mb-4">
        <Link to="/privacy-policy" className="text-blue-400 hover:underline">
          Privacy Policy
        </Link>{" "}
        |{" "}
        <Link to="/terms-of-service" className="text-blue-400 hover:underline">
          Terms of Service
        </Link>{" "}
        |{" "}
        <Link to="/contact" className="text-blue-400 hover:underline">
          Contact Us
        </Link>{" "}
        |{" "}
        <Link to="/how-to-play" className="text-blue-400 hover:underline">
          How to Play
        </Link>
      </div>
      <div>
        <p>
          Stay connected with us on{" "}
          <a
            href="https://www.instagram.com"
            target="_blank"
            className="text-blue-400 hover:underline"
            rel="noopener noreferrer"
          >
            Instagram
          </a>
          .
        </p>
      </div>
    </div>
  );
};

export default Footer;
