import React from "react";
import { Link } from "react-router-dom";
import Button from "../ui/button";

const Online: React.FC = () => {
  return (
    <section>
      <div className="flex flex-col items-center justify-center min-h-screen gap-4 text-white bg-gray-900">
        <h1 className="text-2xl font-bold sm:text-4xl">Find your rival</h1>
        <p className="text-lg">Select matchup option</p>
        <div className="flex gap-4">
          <Button text="Share match code" />
          <Button text="Queue in matchmaking" />
        </div>
        <Link to="/">
          <Button text="Go Back" className="mx-auto mt-6 sm:w-48" />
        </Link>
      </div>
    </section>
  );
};

export default Online;
