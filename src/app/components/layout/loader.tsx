import React from "react";

type Props = {
  text: string;
};

export default function Loader({ text }: Props) {
  return (
    <div className="absolute z-50 w-full h-full aspect-square flex flex-col items-center justify-center bg-gray-900 bg-opacity-90">
      <div className="loader-container flex items-center justify-center">
        <div className="spinner border-t-4 border-blue-500 rounded-full w-16 h-16 animate-spin"></div>
      </div>
      <p className="mt-4 text-lg text-white">{text || "Loading..."}</p>
    </div>
  );
}
