import React from "react";
import { toast } from "sonner";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <div
      id="header"
      className="fixed top-4 left-0 right-0 sm:left-4 sm:right-auto m-auto flex items-center justify-evenly w-64 h-14 z-10 bg-gray-900 bg-opacity-50 border border-gray-800 backdrop-blur rounded-full sm:rounded-tl-none transition-all duration-300 ease-in-out"
    >
      {/* Home Link */}
      <Link to="/" reloadDocument>
        <button className="w-full h-full flex items-end justify-center gap-2 group">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="24"
            height="24"
            strokeWidth="1.5"
          >
            <path d="M5 12l-2 0l9 -9l9 9l-2 0"></path>
            <path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-7"></path>
            <path d="M9 21v-6a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v6"></path>
          </svg>
          <span className="text-white leading-5 group-hover:underline">
            Home
          </span>
        </button>
      </Link>

      {/* Report Link */}
      <Link to="/">
        <button
          className="w-full h-full flex items-end justify-center gap-2 group cursor-not-allowed"
          onClick={() =>
            toast.info("Reporting functionality will be available soon.")
          }
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="24"
            height="24"
            strokeWidth="1.5"
          >
            <path d="M9 9v-1a3 3 0 0 1 6 0v1"></path>
            <path d="M8 9h8a6 6 0 0 1 1 3v3a5 5 0 0 1 -10 0v-3a6 6 0 0 1 1 -3"></path>
            <path d="M3 13l4 0"></path>
            <path d="M17 13l4 0"></path>
            <path d="M12 20l0 -6"></path>
            <path d="M4 19l3.35 -2"></path>
            <path d="M20 19l-3.35 -2"></path>
            <path d="M4 7l3.75 2.4"></path>
            <path d="M20 7l-3.75 2.4"></path>
          </svg>
          <span className="text-white leading-5 group-hover:underline">
            Report
          </span>
        </button>
      </Link>
    </div>
  );
};

export default Header;
