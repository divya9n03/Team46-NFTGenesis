const nextConfig = {
  reactStrictMode: true,
  env: {
      INFURA_IPFS_PROJECT_ID: process.env.INFURA_IPFS_PROJECT_ID,
      INFURA_IPFS_PROJECT_SECRET: process.env.INFURA_IPFS_PROJECT_SECRET,
  },
}

module.exports = nextConfig