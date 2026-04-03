# Development Guidelines

This document outlines the comprehensive development guidelines for the AI Trader project.

## Table of Contents
1. [Installation](#installation)
2. [Code Style](#code-style)
3. [Testing](#testing)
4. [Documentation](#documentation)
5. [Contribution](#contribution)

## Installation
To set up the development environment:
1. Clone the repository:
   ```bash
   git clone https://github.com/zhangyan8216/ai-trader.git
   ```
2. Navigate to the project directory:
   ```bash
   cd ai-trader
   ```
3. Install the necessary dependencies:
   ```bash
   npm install
   ```

## Code Style
Maintain a consistent code style throughout the project:
- Use [ESLint](https://eslint.org/) for JavaScript linting.
- Follow [Airbnb's JavaScript Style Guide](https://github.com/airbnb/javascript).

## Testing
Testing is crucial for maintaining code quality:
- Write unit tests for each module in the `__tests__` directory.
- Use [Jest](https://jestjs.io/) for running tests.
- To run the tests, execute:
  ```bash
  npm test
  ```

## Documentation
Keep documentation up to date:
- Use [JSDoc](https://jsdoc.app/) for documenting code.
- Generate documentation with:
  ```bash
  jsdoc .
  ```

## Contribution
Contributing to this project is welcome. To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Push your changes and create a pull request.

## License
This project is licensed under the MIT License.
