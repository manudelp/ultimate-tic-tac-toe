import React from "react";
import Link from "next/link";
import Button from "@/components/ui/button";

const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 pt-20 space-y-6 ">
      <div className="grid grid-cols-3 mb-6">
        <div className="flex items-center justify-center w-24 h-24 border-b-2 border-r-2 border-white"></div>
        <div className="flex items-center justify-center w-24 h-24 border-b-2 border-l-2 border-r-2 border-white"></div>
        <div className="flex items-center justify-center w-24 h-24 border-b-2 border-l-2 border-white"></div>
        <div className="flex items-center justify-center w-24 h-24 border-t-2 border-b-2 border-r-2 border-white"></div>
        <div className="flex items-center justify-center w-24 h-24 text-6xl font-bold text-white border border-white">
          ?
        </div>
        <div className="flex items-center justify-center w-24 h-24 border-t-2 border-b-2 border-l-2 border-white"></div>
        <div className="flex items-center justify-center w-24 h-24 border-t-2 border-r-2 border-white"></div>
        <div className="flex items-center justify-center w-24 h-24 border-t-2 border-l-2 border-r-2 border-white"></div>
        <div className="flex items-center justify-center w-24 h-24 border-t-2 border-l-2 border-white"></div>
      </div>

      <h1 className="text-5xl font-extrabold text-red-400">
        404 - Page Not Found
      </h1>
      <p className="mt-4 text-lg text-center text-gray-300">
        The page you&#39;re looking for doesn&#39;t exist.
      </p>
      <Link href="/">
        <Button variant="danger" text="Go back home" />
      </Link>
    </div>
  );
};

export default NotFound;
