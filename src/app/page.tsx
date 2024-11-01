"use client";
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import Header from "./components/layout/header";
// import Sidebar from "./components/layout/sidebar";
import Dashboard from "./components/layout/dashboard";
import Footer from "./components/layout/footer";

export default function Home() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return null; // Render nothing on the server
  }

  const version = "0.1.0-alpha-next";

  return (
    <Router>
      <div className="min-h-screen bg-black text-white">
        <p className="absolute right-0 opacity-30">{version}</p>
        {/* <Header /> */}
        <div className="flex">
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
