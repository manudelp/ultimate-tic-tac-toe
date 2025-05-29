// imports
import React, { ReactNode } from "react";

interface ButtonProps {
  text?: string;
  content?: ReactNode;
  variant?: "primary" | "secondary" | "success" | "danger" | "warning";
  className?: string;
  disabled?: boolean;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({
  text,
  content,
  variant,
  className,
  onClick,
  disabled,
}) => {
  // Default to primary variant if none is provided
  variant = variant || "primary";
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full sm:w-64 px-6 py-4 transition-colors rounded 
      ${className || ""} ${
        variant === "primary"
          ? "bg-gray-800 hover:bg-gray-700 text-white"
          : variant === "secondary"
          ? "bg-blue-800 hover:bg-blue-700 text-white"
          : variant === "success"
          ? "bg-green-600 hover:bg-green-500 text-white"
          : variant === "danger"
          ? "bg-red-800 hover:bg-red-700 text-white"
          : variant === "warning"
          ? "bg-yellow-600 hover:bg-yellow-500 text-black"
          : "bg-gray-800 hover:bg-gray-700 text-white"
      }`}
    >
      {content || text}
    </button>
  );
};

export default Button;
