// imports
import React from "react";

interface ButtonProps {
  text: string;
  className?: string;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({ text, className, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-4 transition-colors bg-gray-800 rounded sm:w-64 hover:bg-gray-700 ${
        className || ""
      }`}
    >
      {text}
    </button>
  );
};

export default Button;
