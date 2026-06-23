import type { NextConfig } from "next";

// Configure Turbopack to use the frontend directory as the workspace root.
const nextConfig: NextConfig = {
	turbopack: {
		root: __dirname,
	},
};

export default nextConfig;
