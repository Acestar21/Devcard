import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
     remotePatterns: [
       { hostname: 'avatars.githubusercontent.com' },
       { hostname: 'localhost', port: '8000' },
     ],
  }
};

export default nextConfig;
