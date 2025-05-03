"use client";
import Button from "@/components/ui/button";

export default function Matchmaking() {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-12  min-h-svh">
      <div className="w-full max-w-2xl text-center">
        <h1 className="mb-12 text-3xl font-bold sm:text-5xl ">Matchmaking</h1>

        <div className="p-8 mb-8 bg-gray-800 border border-gray-700 shadow-lg rounded-xl">
          <div className="mb-6 text-yellow-400">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-16 h-16 mx-auto"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <p className="mb-4 text-xl font-semibold">
            Coming soon! Stay tuned for updates.
          </p>
          <p className="text-gray-300">
            In the meantime, you can play locally or create a lobby to play with
            friends.
          </p>
        </div>

        <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Button
            text="Share a Link"
            variant="secondary"
            onClick={() => {
              window.location.href = "/pvp/lobby";
            }}
          />
          <Button
            text="Exit"
            variant="danger"
            onClick={() => {
              window.location.href = "/pvp";
            }}
          />
        </div>
      </div>
    </div>
  );
}
