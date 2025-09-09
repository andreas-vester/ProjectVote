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
*   [ ] Create the `.github/workflows` directory in the project root.
*   [ ] Define a new GitHub Actions workflow file (e.g., `main.yml`) for CI.

### Phase 2: Backend CI Workflow
*   [ ] Add a job for the backend that:
    *   Checks out the code.
    *   Sets up Python environment.
    *   Installs backend dependencies (e.g., `uv sync`).
    *   Runs backend tests (e.g., `uv run pytest`).
    *   Runs backend linting/formatting checks (e.g., `uv run ruff format .`, `uv run ruff check . --fix`).
    *   Runs type checking (e.g., `uv run ty check .`).

### Phase 3: Frontend CI Workflow
*   [ ] Add a job for the frontend that:
    *   Checks out the code.
    *   Sets up Node.js environment.
    *   Installs frontend dependencies (e.g., `npm install`).
    *   Builds the frontend application (e.g., `npm run build`).
    *   Runs frontend tests (if any are implemented).
    *   Runs frontend linting/formatting checks (e.g., `npm run lint`).

### Phase 4: Workflow Triggers
*   [ ] Configure workflows to trigger on `push` to `main` and `pull_request` events.
*   [ ] Ensure appropriate branch filtering for triggers.

### Phase 5: Docker Image Build (Optional)
*   [ ] Consider adding a separate job or steps within existing jobs to:
    *   Build Docker images for both backend and frontend.
    *   Push images to a container registry (e.g., Docker Hub, GitHub Container Registry) on successful builds of the `main` branch.
