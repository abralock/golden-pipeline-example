/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone", // self-contained server in .next/standalone -> copied to dist/ by `make build`
};

export default nextConfig;
