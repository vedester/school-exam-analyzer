// frontend/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/media/**', // Allow media files
      },
      {
        protocol: 'https',
        hostname: 'school-exam-analyzer.onrender.com', 
        pathname: '/media/**', // Allow media files
      },
    ],
  },
};

export default nextConfig;
