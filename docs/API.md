# API Documentation

## Overview
This document provides an overview of the API endpoints available in the AI Trader.

## Endpoints

### 1. Get Market Data
- **Endpoint:** `/api/market_data`
- **Method:** GET
- **Description:** Retrieve current market data for the assets.
- **Response:** Returns a JSON object containing market data.

### 2. Execute Trade
- **Endpoint:** `/api/trade`
- **Method:** POST
- **Description:** Execute a trade for a specified asset.
- **Request Body:** JSON object containing asset, quantity, and type of trade.
- **Response:** Returns a confirmation of the trade execution.

### 3. Get Trade History
- **Endpoint:** `/api/trade_history`
- **Method:** GET
- **Description:** Retrieve the history of past trades executed by the user.
- **Response:** Returns a JSON array of trade history objects.

### 4. Get User Profile
- **Endpoint:** `/api/user_profile`
- **Method:** GET
- **Description:** Retrieve user profile information.
- **Response:** Returns a JSON object containing user details.

## Usage
To use these endpoints, make sure to include the necessary authentication tokens in your requests.

## Contact
For any questions or feedback, please contact support@ai-trader.com.