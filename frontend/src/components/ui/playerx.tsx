import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils"; // Assuming you have a utility function for class names

interface PlayerXProps {
  className?: string;
}

const PlayerX: React.FC<PlayerXProps> = ({ className }) => {
  return (
    <motion.div
      className={cn(className)}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
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
        <path d="M18 6l-12 12" />
        <path d="M6 6l12 12" />
      </svg>
    </motion.div>
  );
};

export default PlayerX;
