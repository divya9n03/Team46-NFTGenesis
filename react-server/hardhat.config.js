require("@nomiclabs/hardhat-waffle");

const fs = require('fs');
// const infuraId = fs.readFileSync(".infuraid").toString().trim() || "";

module.exports = {
  defaultNetwork: "hardhat",
  networks: {
    hardhat: {
      chainId: 1337
    },
    
    mumbai: {
      // Infura
      url: "https://polygon-mumbai.infura.io/v3/b850ba03482c45f4b2bd6f2f4c40a4d2",
      accounts: [`f9bc2ca5a03fb5e73356600d90a60e518d9a4476f684bc3d97f59ee9fa906592`]
    },
    
  },
  solidity: {
    version: "0.8.4",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  }
};

