"use client";
import React, { useEffect, useState } from "react";
import { getLatestCommitHash } from "@/github";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/layout/sidebar";
import Dashboard from "./components/pages/dashboard";
import HowToPlay from "./components/pages/how-to-play";

export default function Home() {
  const [isClient, setIsClient] = useState(false);
  const [version, setVersion] = useState("");

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const commitHash = await getLatestCommitHash();
        setVersion(commitHash.slice(0, 7));
      } catch (error) {
        console.error("Failed to fetch version:", error);
      }
    };

    fetchVersion();
  }, []);

  if (!isClient) return null;

  return (
    <Router>
      <div className="min-h-screen bg-zinc-800 text-white">
        <p className="absolute right-0">1.1-alpha-{version}</p>
        <div className="flex">
          <Sidebar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/how-to-play" element={<HowToPlay />} />
            <Route path="*" element={<h1>Not Found</h1>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}
