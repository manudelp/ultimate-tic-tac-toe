import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,

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
