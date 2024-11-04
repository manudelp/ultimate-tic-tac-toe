import React from "react";
import { Link } from "react-router-dom";

const TermsOfService: React.FC = () => {
  return (
    <div className="container mx-auto py-4 px-6 my-4 max-w-3xl bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Terms of Service
      </h1>
      <p className="text-gray-600 dark:text-gray-300 mb-4 text-sm italic">
        Last updated: November 2024
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        1. Introduction
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        Welcome to Ultimate Tic Tac Toe! These Terms of Service govern your use
        of our game. By accessing or using the game, you agree to be bound by
        these terms.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        2. Use of the Game
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        You may use the game for personal, non-commercial purposes only. You
        agree not to use the game for any unlawful or prohibited activities.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        3. Intellectual Property
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        All content, features, and functionality of the game are the exclusive
        property of Ultimate Tic Tac Toe and its licensors. You may not
        reproduce, distribute, or create derivative works from any part of the
        game without our prior written consent.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        4. User Conduct
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        You agree to use the game in a manner that is lawful and respectful to
        others. You must not engage in any behavior that could harm the game or
        its users.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        5. Termination
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        We reserve the right to terminate or suspend your access to the game at
        any time, without notice, for any reason, including if you violate these
        terms.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        6. Disclaimer of Warranties
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        The game is provided &quot;as is&quot; and &quot;as available&quot;
        without warranties of any kind, either express or implied. We do not
        warrant that the game will be uninterrupted or error-free.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        7. Limitation of Liability
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        In no event shall Ultimate Tic Tac Toe be liable for any indirect,
        incidental, special, or consequential damages arising out of or in
        connection with your use of the game.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        8. Changes to Terms
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        We may update these terms from time to time. We will notify you of any
        changes by posting the new terms on this page. Your continued use of the
        game after any changes constitutes your acceptance of the new terms.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        9. Contact Us
      </h2>
      <p className="text-gray-700 dark:text-gray-200">
        If you have any questions about this Privacy Policy, please contact at{" "}
        <a className="font-medium" href="mailto:support@ultimatetictactoe.com.">
          support@ultimatetictactoe.com
        </a>{" "}
        or using{" "}
        <Link to="/contact" className="text-blue-400 hover:underline">
          the contact form
        </Link>
        .
      </p>
    </div>
  );
};

export default TermsOfService;
