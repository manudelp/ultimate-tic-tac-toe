import React from "react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <div className="absolute bottom-0 left-0 m-4" draggable>
      <Link to="/" reloadDocument>
        <div className="p-4 bg-gray-950 bg-opacity-50 border border-gray-950 backdrop-blur rounded-full">
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
        </div>
      </Link>
    </div>
  );
};

export default Header;
