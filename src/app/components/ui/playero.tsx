import React from "react";

interface PlayerOProps {
  theme: string;
}

const PlayerO: React.FC<PlayerOProps> = ({ theme }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="90%"
      height="90%"
      viewBox="0 0 24 24"
      strokeWidth="1"
      stroke={`${theme === "dark" ? "#ffffff" : "#000000"}`}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
      <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
    </svg>
  );
};

export default PlayerO;
