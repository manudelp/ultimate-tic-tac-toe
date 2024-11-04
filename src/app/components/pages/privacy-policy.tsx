import React from "react";
import { Link } from "react-router-dom";

const PrivacyPolicy: React.FC = () => {
  return (
    <div className="container mx-auto py-4 px-6 my-4 max-w-3xl bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Privacy Policy
      </h1>
      <p className="text-gray-600 dark:text-gray-300 mb-4 text-sm italic">
        Last updated: November 2024
      </p>

      <p className="text-gray-700 dark:text-gray-200 mb-6">
        Welcome to Ultimate Tic Tac Toe. This Privacy Policy explains how we
        collect, use, disclose, and safeguard your information when you visit
        our game. Please read this privacy policy carefully. If you do not agree
        with the terms of this privacy policy, please do not access the game.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        1. Information We Collect
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        We may collect information about you in a variety of ways. The
        information we may collect via the game depends on the content and
        materials you use, and includes:
      </p>
      <ul className="list-disc list-inside space-y-2 mb-6">
        <li className="text-gray-700 dark:text-gray-200">
          <strong>Personal Data:</strong> Personally identifiable information,
          such as your name, email address, and demographic information, that
          you voluntarily give to us when you register with the game or when you
          choose to participate in various activities related to the game.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          <strong>Derivative Data:</strong> Information our servers
          automatically collect when you access the game, such as your IP
          address, your browser type, your operating system, your access times,
          and the pages you have viewed directly before and after accessing the
          game.
        </li>
      </ul>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        2. Use of Your Information
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        Having accurate information about you permits us to provide you with a
        smooth, efficient, and customized experience. Specifically, we may use
        information collected about you via the game to:
      </p>
      <ul className="list-disc list-inside space-y-2 mb-6">
        <li className="text-gray-700 dark:text-gray-200">
          Create and manage your account.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          Compile anonymous statistical data and analysis for use internally or
          with third parties.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          Deliver targeted advertising, coupons, newsletters, and other
          information regarding promotions and the game to you.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          Increase the efficiency and operation of the game.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          Monitor and analyze usage and trends to improve your experience with
          the game.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          Notify you of updates to the game.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          Request feedback and contact you about your use of the game.
        </li>
      </ul>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        3. Disclosure of Your Information
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-4">
        We may share information we have collected about you in certain
        situations. Your information may be disclosed as follows:
      </p>
      <ul className="list-disc list-inside space-y-2 mb-6">
        <li className="text-gray-700 dark:text-gray-200">
          <strong>By Law or to Protect Rights:</strong> If we believe the
          release of information about you is necessary to respond to legal
          process, to investigate or remedy potential violations of our
          policies, or to protect the rights, property, and safety of others, we
          may share your information as permitted or required by any applicable
          law, rule, or regulation.
        </li>
        <li className="text-gray-700 dark:text-gray-200">
          <strong>Third-Party Service Providers:</strong> We may share your
          information with third parties that perform services for us or on our
          behalf, including payment processing, data analysis, email delivery,
          hosting services, customer service, and marketing assistance.
        </li>
      </ul>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        4. Security of Your Information
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-6">
        We use administrative, technical, and physical security measures to help
        protect your personal information. While we have taken reasonable steps
        to secure the personal information you provide to us, please be aware
        that despite our efforts, no security measures are perfect or
        impenetrable, and no method of data transmission can be guaranteed
        against any interception or other type of misuse.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        5. Policy for Children
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-6">
        We do not knowingly solicit information from or market to children under
        the age of 13. If we learn that we have collected information from a
        child under age 13 without verification of parental consent, we will
        delete that information as quickly as possible. If you become aware of
        any data we have collected from children under age 13, please contact at{" "}
        <a className="font-medium" href="mailto:support@ultimatetictactoe.com.">
          support@ultimatetictactoe.com
        </a>{" "}
        or using{" "}
        <Link to="/contact" className="text-blue-400 hover:underline">
          the contact form
        </Link>
        .
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        6. Changes to This Privacy Policy
      </h2>
      <p className="text-gray-700 dark:text-gray-200 mb-6">
        We may update this Privacy Policy from time to time in order to reflect,
        for example, changes to our practices or for other operational, legal,
        or regulatory reasons. We will notify you of any changes by posting the
        new Privacy Policy on this page. You are advised to review this Privacy
        Policy periodically for any changes. Changes to this Privacy Policy are
        effective when they are posted on this page.
      </p>

      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-3">
        Contact Us
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

export default PrivacyPolicy;
