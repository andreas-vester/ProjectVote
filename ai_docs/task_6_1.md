# Task 6.1: Unified Docker-based Deployment

## Goal
Define and implement a unified, container-based deployment strategy for the entire application (backend and frontend) using Docker and Docker Compose.

## Plan
1.  Containerize the frontend application.
2.  Create a `docker-compose.yml` to orchestrate all services.
3.  Configure inter-service communication and environment variables.
4.  Establish a local development environment with MailHog.
5.  Document the deployment process.

## Tasks

### Phase 1: Frontend Containerization
*   [x] Create a multi-stage `Dockerfile` for the frontend that builds the React app and serves it with Nginx.

### Phase 2: Docker Compose Setup
*   [x] Create a `docker-compose.yml` file at the project root.
*   [x] Define a `backend` service using the existing `Dockerfile`.
*   [x] Define a `frontend` service using the new frontend `Dockerfile`.
*   [x] Add a `mailhog` service for local email testing.

### Phase 3: Configuration
*   [x] Update environment variables (`.env.example`) for Docker networking (e.g., `VITE_API_BASE_URL`, `FRONTEND_URL`).
*   [x] Ensure services can communicate with each other using service names.

### Phase 4: Documentation
*   [x] Add instructions to `README.md` on how to run the application using `docker-compose`.
