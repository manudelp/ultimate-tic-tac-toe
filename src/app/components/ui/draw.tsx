import React from "react";

interface DrawProps {
  theme: string;
}

const Draw: React.FC<DrawProps> = ({ theme }) => {
  return (
    <svg width="40" height="40" xmlns="http://www.w3.org/2000/svg">
      <line
        x1="10"
        y1="20"
        x2="30"
        y2="20"
        stroke={theme === "dark" ? "#ffffff" : "#000000"}
        strokeWidth="1"
      />
    </svg>
  );
};

export default Draw;
