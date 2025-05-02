import React from "react";

interface DrawProps {
  theme: string;
}

const Draw: React.FC<DrawProps> = ({ theme }) => {
  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 40 40"
      xmlns="http://www.w3.org/2000/svg"
    >
      <line
        x1="10"
        y1="20"
        x2="30"
        y2="20"
        stroke={theme === "dark" ? "#ffffff" : "#000000"}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default Draw;
