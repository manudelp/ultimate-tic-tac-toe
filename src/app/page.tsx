"use client";
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/layout/header";
import Sidebar from "./components/layout/sidebar";
import Dashboard from "./components/layout/dashboard";
import Footer from "./components/layout/footer";

export default function Home() {
  return (
    <Router>
      <div className="min-h-screen bg-black text-white">
        <Header />
        <Sidebar />
        <div className="flex">
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
