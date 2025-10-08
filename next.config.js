/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    optimizePackageImports: ['axios']
  },
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8001'
  }
}

module.exports = nextConfig