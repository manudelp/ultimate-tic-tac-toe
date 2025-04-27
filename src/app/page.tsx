"use client";
import React, { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { checkConnection } from "@/api";
import Dashboard from "./components/pages/dashboard";
import Lobby from "./components/pages/lobby";
import HowToPlay from "./components/pages/how-to-play";
import PrivacyPolicy from "./components/pages/privacy-policy";
import TermsOfService from "./components/pages/terms-of-service";
import Footer from "./components/layout/footer";
import Header from "./components/layout/header";
import ContactUs from "./components/pages/contact-us";
import NotFound from "./components/pages/not-found";
export default function Home() {
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [isClient, setIsClient] = useState(false);
  const pathname = usePathname();

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

  const renderPage = () => {
    if (pathname === "/") {
      return <Dashboard isBackendConnected={isBackendConnected} />;
    } else if (pathname === "/how-to-play") {
      return <HowToPlay />;
    } else if (pathname === "/privacy-policy") {
      return <PrivacyPolicy />;
    } else if (pathname === "/terms-of-service") {
      return <TermsOfService />;
    } else if (pathname === "/lobby") {
      return <Lobby />;
    } else if (pathname === "/contact") {
      return <ContactUs />;
    } else {
      return <NotFound />;
    }
  };

  if (!isClient) return null;
  return (
    <div className="text-white bg-gray-900 min-h-svh">
      {isClient && (
        <>
          <Header />
          {renderPage()}
          <Footer isBackendConnected={isBackendConnected} />
        </>
      )}
    </div>
  );
}
