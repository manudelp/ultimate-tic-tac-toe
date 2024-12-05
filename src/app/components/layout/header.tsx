import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Modal } from "@/app/components/ui/modal";
import { LoginForm } from "@/components/ui/login-form";

const Header = () => {
  const [isModalOpen, setModalOpen] = useState(false);
  const [userName, setUserName] = useState<string | null>(null);

  useEffect(() => {
    const storedName = localStorage.getItem("name");
    if (storedName) {
      setUserName(storedName);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("name");
    setUserName(null);
    window.location.reload();
  };

  return (
    <>
      <div
        id="header"
        className="fixed top-4 left-0 right-0 z-50 sm:left-4 sm:right-auto mx-4 sm:m-auto flex items-center justify-evenly bg-gray-900 bg-opacity-50 border border-gray-800 backdrop-blur rounded-full sm:rounded-tl-none transition"
      >
        {/* Home Link */}
        <Link to="/" reloadDocument>
          <button className="flex items-center gap-2 p-4 rounded-full hover:bg-white hover:text-black transition group">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
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
            <span className="text-white group-hover:text-black">Home</span>
          </button>
        </Link>

        {/* Condicional: Mostrar nombre del usuario o botón de Login */}
        {userName ? (
          <div className="flex items-center gap-2 p-4 rounded-full">
            <span>Welcome, {userName}.</span>
            <button
              title="Logout"
              className="ml-4 text-white hover:text-red-600 transition"
              onClick={handleLogout}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                width="24"
                height="24"
                strokeWidth="1.5"
              >
                <path d="M14 8v-2a2 2 0 0 0 -2 -2h-7a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h7a2 2 0 0 0 2 -2v-2"></path>
                <path d="M9 12h12l-3 -3"></path>
                <path d="M18 15l3 -3"></path>
              </svg>
            </button>
          </div>
        ) : (
          <button
            className="flex items-center gap-2 p-4 rounded-full hover:bg-white hover:text-black transition group"
            onClick={() => setModalOpen(true)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="24"
              height="24"
              strokeWidth="2"
            >
              <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0"></path>
              <path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2"></path>
            </svg>
            <span className="text-white group-hover:text-black">
              Login / Register
            </span>
          </button>
        )}
      </div>

      {/* Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setModalOpen(false)}>
        <LoginForm />
      </Modal>
    </>
  );
};

export default Header;
