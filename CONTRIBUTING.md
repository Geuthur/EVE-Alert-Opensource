# Contributing to This Project

Thank you for considering contributing to our project! Here are some guidelines to help you get started.

## Getting Started

1. **Fork the repository**: Click the "Fork" button at the top right of the repository page.

1. **Clone your fork**: Clone your forked repository to your local machine.

   ```sh
   git clone https://github.com/geuthur/EVE-Alert-Opensource.git
   ```

1. **Set up the upstream remote**: Add the original repository as a remote to keep your fork up to date.

   ```sh
   git remote add upstream https://github.com/geuthur/EVE-Alert-Opensource.git
   ```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality and consistency. Please make sure you have pre-commit installed and set up.

1. **Install pre-commit**: If you don't have pre-commit installed, you can install it using pip.

   ```sh
   pip install pre-commit
   ```

1. **Install the hooks**: Run the following command to install the pre-commit hooks.

   ```sh
   pre-commit install
   ```

1. **Use Pre Commit**

   Check all files

   ```sh
   pre-commit run --all-files
   ```

   If you want only one of the hooks like `eslint`

   ```sh
   pre-commit run eslint
   ```

## Branching und Contributing via Pull Requests

Before creating a pull request, make sure that you have forked the repository and are working on your fork. This ensures that your changes are isolated and do not affect the original repository until they are reviewed and merged.

The `master` branch should always be kept up to date to avoid conflicts. This means that all changes integrated into the `master` branch should be thoroughly reviewed and tested before being merged. Regular updates and synchronizations with the `master` branch help to identify and resolve potential conflicts early.

Before creating a new feature, an issue should always be opened first. This serves to start a discussion about the planned feature and ensure that all team members are informed about the planned changes. Through discussion, potential problems and improvements can be identified and considered early. This promotes a collaborative working approach and contributes to the quality and consistency of the project.
