# Task 3.1: Environment Variable Setup

## Goal
Establish a system for managing environment-specific variables securely and efficiently.

## Tasks
*   [x] A `.env` file is used to store secrets and environment-specific settings.
*   [x] The `.env` file is included in `.gitignore` to prevent committing it.
*   [x] A `.env.example` file is created to serve as a template for required variables.
*   [x] The `python-dotenv` library is added to the project to load variables from the `.env` file.
*   [x] A `.env.local` file is used for local development overrides.
*   [x] The `.env.local` file is included in `.gitignore`.
*   [x] An `APP_ENV` environment variable is used to switch between `development`, `testing`, and `production` environments.
*   [x] The application is configured to load the correct `.env` file based on `APP_ENV`.
