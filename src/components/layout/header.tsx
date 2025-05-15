// import { useState, useEffect } from "react";
import Link from "next/link";
// import { Modal } from "@/app/components/ui/modal";
// import { toast } from "sonner";

const Header = () => {
  // const [isModalOpen, setModalOpen] = useState(false);
  // const [userName, setUserName] = useState<string | null>(null);

  // useEffect(() => {
  //   const storedName = localStorage.getItem("name");
  //   if (storedName) {
  //     setUserName(storedName);
  //   }
  // }, []);

  // const handleLogout = () => {
  //   localStorage.removeItem("token");
  //   localStorage.removeItem("name");
  //   setUserName(null);
  //   window.location.reload();
  // };

  return (
    <>
      <div
        id="header"
        className="fixed left-0 right-auto z-50 flex items-center m-auto mx-4 transition bg-opacity-50 border border-gray-800 rounded-full rounded-tl-none top-2 sm:top-4 sm:left-4 justify-evenly backdrop-blur"
      >
        {/* Home Link */}
        <Link href="/">
          <button className="flex items-center gap-2 p-4 transition rounded-full rounded-tl-none hover:bg-white hover:text-black group">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
              />
            </svg>
            <span className="text-white group-hover:text-black">Home</span>
          </button>
        </Link>

        {/* Condicional: Mostrar nombre del usuario o botón de Login */}
        {/* {userName ? (
          <div className="flex items-center gap-2 p-4 rounded-full">
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
            <span>{userName}</span>
            <button
              title="Logout"
              className="ml-4 text-white transition hover:text-red-600"
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
            className="flex items-center gap-2 p-4 transition rounded-full hover:bg-white hover:text-black group"
            onClick={() =>
              isBackendConnected
                ? setModalOpen(true)
                : toast.error("Can't login if server is offline.", {
                    description: "Wait a few seconds and try again.",
                    action: {
                      label: "Reload",
                      onClick: () => window.location.reload(),
                    },
                  })
            }
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
        )} */}
      </div>

      {/* Modal */}
      {/* <Modal isOpen={isModalOpen} onClose={() => setModalOpen(false)}>
        <LoginForm />
      </Modal> */}
    </>
  );
};

export default Header;
