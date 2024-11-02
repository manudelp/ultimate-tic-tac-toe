"use client";
import React, { useEffect, useState } from "react";
import { getLatestCommitHash } from "@/github";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import Header from "./components/layout/header";
// import Sidebar from "./components/layout/sidebar";
import Dashboard from "./components/layout/dashboard";
import Footer from "./components/layout/footer";

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
      <div className="min-h-screen bg-black text-white">
        <p className="absolute right-0 opacity-30">1.1-alpha-{version}</p>
        {/* <Header /> */}
        <div>
          {/* <Sidebar /> */}
          <Routes>
            <Route path="/" element={<Dashboard />} />
            {/* <Route path="/how-to-play" element={<HowToPlay />} /> */}
            <Route path="*" element={<h1>Not Found</h1>} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}
