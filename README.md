# ProjectVote

ProjectVote is a funding application management system designed to streamline the process of submitting, reviewing, and deciding on project funding requests for associations and organizations.

## Features

-   **Application Submission:** User-friendly form for submitting new funding requests.
-   **Token-Based Voting:** Secure, unique voting links for board members to review and cast votes.
-   **Automated Decision Processing:** Automatic status updates and notifications based on board votes.
-   **Application Archive:** A historical record of all funding applications and their outcomes.

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ProjectVote
    ```

2.  **Create environment files:**
    *   Create a `.env` file in the project root by copying the `.env.example`. Update the `BOARD_MEMBERS` and other variables as needed.
    *   Create a `.env` file in `src/projectvote/frontend` by copying the `src/projectvote/frontend/.env.example`.

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the application:**
    *   **Frontend:** [http://localhost:5173](http://localhost:5173)
    *   **Backend API:** [http://localhost:8008](http://localhost:8008)


The application should now be running. The first time you run the application, Docker Compose will build the images, which may take a few minutes.

## Database

The application uses a SQLite database to store application data.

### Location and Persistence

The database is stored in the `data` directory at the root of the project. This is achieved using a bind mount in `docker-compose.yml`, which maps the `./data` directory on your host machine to the `/app/data` directory inside the `backend` container.

This ensures the database file (`applications.db`) is directly accessible on your filesystem and persists across container restarts.

### Accessing the Database

Since the database file is on your host machine at `data/applications.db`, you can open it using any standard SQLite database tool. There is no need to connect to the running container.
