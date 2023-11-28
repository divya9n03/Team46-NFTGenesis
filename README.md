# Team46-NFTGenesis
This is the official repository for the UE20CS461A Capstone project of Team 46.<br><br>The team members are:
| Name | SRN |
| --------------- | --------------- |
| Divya N   | PES2UG20CS114    |
| Eeshan Dhawan    | PES2UG20CS117    |
| H Sarath Sundar    | PES2UG20CS131    |
| Harshit Jain    | PES2UG20CS136   |

<br>
NFTGenesis is a platform built to minimize cyber frauds and to ensure NFT (Non-Fungible Token) authenticity using a sophisticated approach to crypto-steganography infused with deep learning. It is an integrated web application that enables NFT authentication, predictive pricing analysis, keyword based NFT creation and in a nutshell acts as a robust marketplace for NFT minting.
<br><br>

Link to dataset: https://drive.google.com/drive/u/0/folders/1y4gtgzEAhovCKP1-3d-jQIBNu28bg7Mw

# Steps to run the web application
### Installation
Clone the NFTGenesis repository onto your local system.<br>
Download required models from the drive link : https://drive.google.com/drive/folders/1DqmxLBCGJQppWkhzhpPhjg6XNwg6ittX and add the required path variables in the app.py file.

### Step 1 
Start the flask server using the command ```python app.py```<br>
### Step 2
To run the node server first install all the required npm modules using ```npm i```
Next, run ```npx hardhat run scripts/deploy.js --network localhost```
Finally, run ``` npm run dev``` command to deploy the node server<br>
### Step 3
Open localhost:3000 in your convenient browser to launch NFTGenesis. Create an account and register yourself.
### Step 4
NFTGenesis offers different token utilities.<br>
* **NFT Generator:** Input a keyword or a phrase to generate a token based on the same. This generation is performed using a fine-tuned stable diffusion model.<br><br>
* **NFT Authenticator:** Input an NFT to generate an authenticated NFTGenesis certified token using a Generative Adversarial Network (GAN).<br><br>
* **NFT Price Predictor:** Feed an NFT to the augmented ResNet50 model to understand the market price and rarity value of your token.<br><br>
* **NFT Minter:** Input an NFT to buy,sell or bid NFTs. Browse through NFTGenesis dashboard to trade tokens after connecting to your verified crypto-wallet.<br><br>
* **NFT Validator:** To ensure the authenticity and legitimacy of a token before buying/selling from another token holder, validate whether the token is NFTGenesis certified or not.<br><br>

