import React, { useState } from "react";
import Image from "next/image";
import { Link } from "react-router-dom";

export default function Header() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="sm:hidden absolute w-full p-4 bg-gray-950">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2 text-white">
          <Image src="/icon.png" alt="Logo" width={30} height={30} />
          Ultimate Tic TacToe
        </div>
        <button
          onClick={toggleMenu}
          className={`text-white transition-transform duration-300 ${
            isOpen ? "rotate" : ""
          }`}
        >
          {isOpen ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16m-7 6h7"
              />
            </svg>
          )}
        </button>
      </div>
      <div
        className={`mt-2 transition-all duration-300 ease-in-out ${
          isOpen
            ? "max-h-screen opacity-100 pointer-events-auto"
            : "max-h-0 opacity-0 pointer-events-none"
        }`}
      >
        <ul className="list-none">
          <Link to="/">
            <li className="p-2 hover:bg-gray-800 transition-colors duration-300">
              Home
            </li>
          </Link>
          <Link to="/how-to-play">
            <li className="p-2 hover:bg-gray-800 transition-colors duration-300">
              How to Play
            </li>
          </Link>
        </ul>
      </div>
    </div>
  );
}
