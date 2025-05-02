import React from "react";
import { motion } from "framer-motion";

interface PlayerOProps {
  theme: string;
}

const PlayerO: React.FC<PlayerOProps> = ({ theme }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="grid place-items-center"
    >
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
    </motion.div>
  );
};

export default PlayerO;
