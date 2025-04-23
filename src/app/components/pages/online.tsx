import React from "react";
import Button from "../ui/button";

interface OnlineProps {
  isBackendConnected: boolean;
}

const Online: React.FC<OnlineProps> = ({ isBackendConnected }) => {
  return (
    <section>
      <div className="flex flex-col items-center justify-center min-h-screen gap-4 text-white bg-gray-900">
        <h1 className="text-4xl font-bold">Online</h1>
        <div className="flex gap-4">
          <Button text="Share match code" />
          <Button text="Queue for a match" />
        </div>
      </div>
    </section>
  );
};

export default Online;
