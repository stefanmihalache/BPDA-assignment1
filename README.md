# Assignment 1 - Trading Card Games

In this project, I have developed an API solution using FastAPI deployed in a Docker container. The API leverages the MultiversX Python SDK to interact with a custom smart contract deployed on the MultiversX blockchain.

The smart contract enables the creation and exchange of NFTs (Non-Fungible Tokens), each representing a unique trading card in the game. This project showcases a system where NFTs are minted with specific attributes (e.g., name, rarity, power), can be exchanged between users, and ensures that all transactions are secure and validated.

## 1. Contract Interactions
### Key functionalities:

issueNft: Allows the owner to issue an NFT collection.

createNftWithAttributes: Generates NFTs with specified attributes (e.g., name, class, rarity, power).

getYourNftCardProperties: Retrieves randomized NFT card properties for the caller.

exchangeNft: Facilitates NFT trading, ensuring compatibility of card attributes.

## 2. Proposed Solution

This FastAPI application provides an interface for interacting with a smart contract deployed on the MultiversX blockchain, specifically designed for a Trading Card Game. The application enables users to mint, exchange, and query NFTs (Non-Fungible Tokens) that represent unique trading cards in the game. The solution uses the MultiversX Python SDK to handle blockchain interactions and utilizes Docker for containerized deployment, ensuring scalability and portability.

Core Features
The FastAPI application exposes several key endpoints for managing NFTs and interacting with the underlying smart contract:

### Root Endpoint (/): 
A simple welcome message that directs users to the Swagger UI for API documentation.
### Assigned NFT (/assigned/nft/): 
Allows users to retrieve the properties of the NFT that has been assigned to them for trading.
### Smart Contract Data (/smart-contract/data/): 
Provides information about the current state of the smart contract and the assigned NFT, including the specific card properties.
### Create NFT Collection (/collection/): 
Facilitates the creation of a new NFT collection, allowing the owner to issue a batch of NFTs for the game.
### Add Roles to Collection (/collection/add-roles/):
Allows the owner to assign roles to the NFT collection, which could be used for managing access or permissions in the game.
### Create NFT (/nft/): 
Allows the creation of a new NFT (Trading Card) with attributes like name, rarity, power, and other characteristics.
### Get NFT (/nft/): 
Retrieves information about a newly minted NFT, including its nonce, for use in game transactions.
### Exchange NFT (/nft/exchange/): 
Facilitates the trading of NFTs between users, validating the compatibility of their cards based on predefined attributes.

Background Task Handling: As blockchain transactions are asynchronous, certain functions like waiting for a transaction to complete (e.g., when minting an NFT or creating a collection) are handled using background tasks in FastAPI, ensuring smooth user experience without blocking the main API flow.

Docker Deployment: The FastAPI app is containerized using Docker, ensuring that the application is portable and can be easily deployed across various environments without dependency issues.

Error Handling and Logging: The application includes robust error handling and logging mechanisms using the LOG object to ensure that transaction processes are tracked, and issues can be quickly debugged.

