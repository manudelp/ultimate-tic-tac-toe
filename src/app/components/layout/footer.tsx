"use client";
import React, { useEffect } from "react";

const Footer: React.FC = () => {
  useEffect(() => {
    const year = new Date().getFullYear();
    if (typeof window !== "undefined") {
      const yearElement = document.getElementById("year");
      if (yearElement) {
        yearElement.innerHTML = year.toString();
      }
    }
  }, []);

  return (
    <div className="fixed bottom-0 inset-x-0 p-2 text-sm bg-black text-white text-center">
      <p>
        &copy; <span id="year"></span> All rights reserved |{" "}
        <a
          href="https://www.linkedin.com/in/manuel-delpino/"
          target="_blank"
          className="text-blue-500 hover:underline"
          rel="noopener noreferrer"
        >
          Manuel Delpino
        </a>{" "}
        &{" "}
        <a
          href="https://www.linkedin.com/in/manuel-meiriño-7b9214331/"
          target="_blank"
          className="text-blue-500 hover:underline"
          rel="noopener noreferrer"
        >
          Manuel Meiriño
        </a>
      </p>
    </div>
  );
};

export default Footer;
