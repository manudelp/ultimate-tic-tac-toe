import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-6">
            <div className="grid grid-cols-3 mb-6">
                <div className="w-24 h-24 flex items-center justify-center border-r-2 border-b-2 border-white"></div>
                <div className="w-24 h-24 flex items-center justify-center border-l-2 border-b-2 border-r-2 border-white"></div>
                <div className="w-24 h-24 flex items-center justify-center border-l-2 border-b-2 border-white"></div>
                <div className="w-24 h-24 flex items-center justify-center border-t-2 border-r-2 border-b-2 border-white"></div>
                <div className="w-24 h-24 flex items-center justify-center border border-white text-white text-6xl font-bold">?</div>
                <div className="w-24 h-24 flex items-center justify-center border-l-2 border-t-2 border-b-2 border-white"></div>
                <div className="w-24 h-24 flex items-center justify-center border-t-2 border-r-2 border-white"></div>
                <div className="w-24 h-24 flex items-center justify-center border-l-2 border-t-2 border-r-2 border-white"></div>
                <div className="w-24 h-24 flex items-center justify-center border-l-2 border-t-2 border-white"></div>
            </div>
            <h1 className="text-5xl font-extrabold text-red-400">404 - Page Not Found</h1>
            <p className="mt-4 text-lg text-gray-300 text-center">
                The page you're looking for doesn't exist.
            </p>
            <Link
                to="/"
                className="mt-6 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-lg hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
            >
                Go Back to Home
            </Link>
        </div>
    );
};

export default NotFound;