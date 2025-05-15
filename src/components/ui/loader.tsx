import React from "react";

interface LoaderProps {
  size?: "small" | "medium" | "large" | string;
}

const Loader: React.FC<LoaderProps> = ({ size = "medium" }) => {
  const sizeMap = {
    small: "8",
    medium: "14",
    large: "20",
  };

  // Use the mapped size or the raw value if it's not in the map
  const actualSize = sizeMap[size as keyof typeof sizeMap] || size;

  return (
    <div className="flex items-center justify-center">
      <div
        className={`animate-spin rounded-full h-${actualSize} w-${actualSize} border-t-4 border-blue-500`}
      ></div>
    </div>
  );
};

export default Loader;
