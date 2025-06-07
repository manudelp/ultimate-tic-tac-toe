/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["upload.wikimedia.org"],
  },
  experimental: {
    esmExternals: "loose",
  },
  // Ensure auth callback page is not statically generated
  async generateStaticParams() {
    return [];
  },
  // Handle auth callback route specifically
  async rewrites() {
    return [
      {
        source: "/auth/callback",
        destination: "/auth/callback",
      },
    ];
  },
  // Disable static optimization for auth pages
  async headers() {
    return [
      {
        source: "/auth/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "no-cache, no-store, must-revalidate",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
