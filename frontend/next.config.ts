import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  turbopack: {
    root: __dirname,
  },

  async rewrites() {
    return [
      {
        source: "/:path*",
        destination: "/:path*", // This allows Next.js to handle all paths dynamically
      },
    ];
  },
};

export default nextConfig;
