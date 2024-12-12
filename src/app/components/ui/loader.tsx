import React from "react";

const Loader: React.FC = () => {
  return (
    <div className="flex items-center justify-center">
      <div className="animate-spin rounded-full h-14 w-14 border-t-4 border-blue-500"></div>
    </div>
  );
};

export default Loader;
