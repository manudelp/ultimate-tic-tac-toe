import { Link } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
} from "@/components/ui/dropdown-menu";
import { LoginForm } from "@/components/ui/login-form";

const Header = () => {
  return (
    <div
      id="header"
      className="fixed top-4 left-0 right-0 sm:left-4 sm:right-auto m-auto flex items-center justify-evenly w-64 h-14 z-10 bg-gray-900 bg-opacity-50 border border-gray-800 backdrop-blur rounded-full sm:rounded-tl-none transition-all duration-300 ease-in-out"
    >
      {/* Home Link */}
      <Link to="/" reloadDocument>
        <button className="w-full h-full flex items-center gap-2">
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
          <span className="text-white">Home</span>
        </button>
      </Link>

      {/* Login Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex items-center gap-2">
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
            <span className="text-white">Login</span>
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-80 p-0 border-none rounded-none">
          <LoginForm />
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default Header;
