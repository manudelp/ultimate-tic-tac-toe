import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface DrawProps {
  className?: string;
}

const Draw: React.FC<DrawProps> = ({ className }) => {
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
        <line x1="6" y1="12" x2="18" y2="12" />
      </svg>
    </motion.div>
  );
};

export default Draw;
