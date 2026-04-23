import Link from "next/link";

const Footer: React.FC = () => {
  return (
    <footer className="flex flex-col items-center justify-center w-full gap-2 p-8 text-sm text-center text-gray-400 bg-gray-950">
      <p>
        &copy; {new Date().getFullYear()} Ultimate Tic Tac Toe. All rights
        reserved.
      </p>
      <p>
        Developed by{" "}
        <a
          href="https://www.linkedin.com/in/manuel-delpino/"
          target="_blank"
          className="text-blue-400 hover:underline"
          rel="noopener noreferrer"
        >
          Manuel Delpino
        </a>{" "}
        &{" "}
        <a
          href="https://www.linkedin.com/in/manuel-meiriño-7b9214331/"
          target="_blank"
          className="text-blue-400 hover:underline"
          rel="noopener noreferrer"
        >
          Manuel Meiriño
        </a>
      </p>
      <div className="flex gap-2">
        <Link href="/privacy-policy" className="hover:text-white transition-colors">
          Privacy Policy
        </Link>
        <span>|</span>
        <Link href="/terms-of-service" className="hover:text-white transition-colors">
          Terms of Service
        </Link>
        <span>|</span>
        <Link href="/how-to-play" className="hover:text-white transition-colors">
          How to Play
        </Link>
      </div>
    </footer>
  );
};

export default Footer;
