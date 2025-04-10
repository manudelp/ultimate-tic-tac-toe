"use client";
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { checkConnection } from "@/api";
import Dashboard from "./components/pages/dashboard";
import HowToPlay from "./components/pages/how-to-play";
import PrivacyPolicy from "./components/pages/privacy-policy";
import TermsOfService from "./components/pages/terms-of-service";
import Footer from "./components/layout/footer";
import Header from "./components/layout/header";
import ContactUs from "./components/pages/contact-us";

export default function Home() {
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Check backend connection
  useEffect(() => {
    const checkBackendConnection = async () => {
      const isConnected = await checkConnection();
      setIsBackendConnected(isConnected);
    };

    checkBackendConnection();
  }, []);

  if (!isClient) return null;
  return (
    <Router>
      <div className="min-h-svh bg-gray-900 text-white">
        <Header />
        <Routes>
          <Route
            path="/"
            element={<Dashboard isBackendConnected={isBackendConnected} />}
          />
          <Route path="/how-to-play" element={<HowToPlay />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/terms-of-service" element={<TermsOfService />} />
          <Route path="/contact" element={<ContactUs />} />
          <Route path="*" element={<h1>Not Found</h1>} />
        </Routes>
        <Footer isBackendConnected={isBackendConnected} />
      </div>
    </Router>
  );
}
