# Task 3.2: Central Configuration Module

## Goal
Create a centralized, type-safe module for accessing application configuration.

## Tasks
*   [x] A `config.py` module is created in the backend.
*   [x] Pydantic is used within the module to define, validate, and expose all configuration settings loaded from the environment.
*   [x] The application consistently uses this module to access configuration instead of directly accessing environment variables.
*   [x] The `Settings` object is created once using a dependency and injected into the parts of the application that need it, ensuring consistent configuration.
