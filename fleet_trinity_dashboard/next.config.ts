import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable StrictMode: its mount-unmount-remount cycle creates duplicate WebGL
  // contexts that exhaust Chrome's limit, causing "Context Lost" in Three.js
  reactStrictMode: false,
};

export default nextConfig;
