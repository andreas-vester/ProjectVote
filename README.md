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
