/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  async rewrites() {
    return [
      // {
      //   source: '/api/:path*',
      //   destination: 'http://localhost:8000/api/:path*', // 指向后端API
      // },
    ];
  },
};

export default nextConfig; 