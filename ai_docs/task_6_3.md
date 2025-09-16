# Task 6.3: Continuous Integration (GitHub Actions)

## Goal
Automate the build, test, and deployment processes using GitHub Actions to ensure code quality and efficient delivery.

## Plan
1.  Set up a basic GitHub Actions workflow.
2.  Configure separate workflows for backend and frontend.
3.  Integrate existing testing and linting commands into the workflows.
4.  Consider adding steps for Docker image building and pushing.

## Tasks

### Phase 1: Workflow Setup
*   [x] Create the `.github/workflows` directory in the project root.
*   [x] Define a new GitHub Actions workflow file (e.g., `main.yml`) for CI.

### Phase 2: Backend CI Workflow
*   [x] Add a job for the backend that:
    *   [x] Checks out the code.
    *   [x] Sets up Python environment.
    *   [x] Installs backend dependencies (e.g., `uv sync`).
    *   [x] Runs backend tests (e.g., `uv run pytest`).
    *   [x] Runs backend linting/formatting checks (e.g., `uv run ruff format .`, `uv run ruff check . --fix`).
    *   [x] Runs type checking (e.g., `uv run ty check .`).

### Phase 3: Frontend CI Workflow
*   [x] Add a job for the frontend that:
    *   [x] Checks out the code.
    *   [x] Sets up Node.js environment.
    *   [x] Installs frontend dependencies (e.g., `npm install`).
    *   [x] Builds the frontend application (e.g., `npm run build`).
    *   [x] Runs frontend tests (if any are implemented).
    *   [x] Runs frontend linting/formatting checks (e.g., `npm run lint`).

### Phase 4: Workflow Triggers
*   [x] Configure workflows to trigger on `push` to `main` and `pull_request` events.
*   [x] Ensure appropriate branch filtering for triggers.

### Phase 5: Docker Image Build (Optional)
*   [x] Consider adding a separate job or steps within existing jobs to:
    *   [x] Build Docker images for both backend and frontend.
    *   [x] Push images to a container registry (e.g., Docker Hub, GitHub Container Registry) on successful builds of the `main` branch.
