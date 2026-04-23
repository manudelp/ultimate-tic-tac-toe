import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils"; // Assuming you have a utility function for class names

interface PlayerOProps {
  className?: string;
}

const PlayerO: React.FC<PlayerOProps> = ({ className }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={cn("grid place-items-center", className)}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="100%"
        height="100%"
        viewBox="0 0 24 24"
        strokeWidth="1"
        stroke="currentColor"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <circle cx="12" cy="12" r="7.5" />
      </svg>
    </motion.div>
  );
};

export default PlayerO;
