import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/v1/:path*', // 指向后端API
      },
    ];
  },
};

export default nextConfig;
