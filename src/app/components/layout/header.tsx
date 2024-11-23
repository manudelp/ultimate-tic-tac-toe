import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const positions = {
  topLeft: "top-0 left-0",
  topRight: "top-0 right-0",
  bottomLeft: "bottom-0 left-0",
  bottomRight: "bottom-0 right-0",
};

const Header = () => {
  const [position, setPosition] = useState<keyof typeof positions>(() => {
    const savedPosition = localStorage.getItem("headerPosition");
    return (savedPosition as keyof typeof positions) || "bottomRight";
  });

  const handleDragEnd = (e: { clientX: number; clientY: number }) => {
    const { clientX, clientY } = e;
    const { innerWidth, innerHeight } = window;

    let newPosition: keyof typeof positions;
    if (clientX < innerWidth / 2 && clientY < innerHeight / 2) {
      newPosition = "topLeft";
    } else if (clientX >= innerWidth / 2 && clientY < innerHeight / 2) {
      newPosition = "topRight";
    } else if (clientX < innerWidth / 2 && clientY >= innerHeight / 2) {
      newPosition = "bottomLeft";
    } else {
      newPosition = "bottomRight";
    }

    setPosition(newPosition);
    localStorage.setItem("headerPosition", newPosition);
  };

  useEffect(() => {
    const headerElement = document.querySelector(".absolute.m-4");
    if (
      headerElement &&
      performance.navigation.type === performance.navigation.TYPE_NAVIGATE
    ) {
      headerElement.classList.add("animate-bounce");
      const timeout = setTimeout(() => {
        headerElement.classList.remove("animate-bounce");
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [position]);

  return (
    <div
      className={`absolute m-4 ${positions[position]}`}
      draggable
      onDragEnd={handleDragEnd}
    >
      <Link to="/" reloadDocument>
        <div className="p-4 bg-gray-950 transition-colors duration-300 rounded-full">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="24"
            height="24"
            strokeWidth="1.5"
          >
            <path d="M5 12l-2 0l9 -9l9 9l-2 0"></path>
            <path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-7"></path>
            <path d="M9 21v-6a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v6"></path>
          </svg>
        </div>
      </Link>
    </div>
  );
};

export default Header;
