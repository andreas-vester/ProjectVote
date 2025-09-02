# Task 6.1: Backend Deployment Strategy

## Goal
Define and implement a strategy for deploying the backend API to a production environment, ensuring scalability, reliability, and security.

## Plan
1.  Choose a deployment platform.
2.  Containerize the backend application.
3.  Configure environment variables and secrets management.
4.  Set up continuous integration/continuous deployment (CI/CD) pipeline.

## Tasks

### Phase 1: Platform Selection
*   [x] Evaluate potential deployment platforms (e.g., Heroku, AWS EC2/ECS, Google Cloud Run, Azure App Service, a private VPS).
*   [x] Consider factors like cost, scalability, ease of management, and existing infrastructure.

#### Evaluation Summary
After reviewing several options, a decision was made based on the project's specific needs, particularly GDPR (DSGVO) compliance and long-term continuity.

The following table summarizes the cost of the leading public cloud candidates:

| Feature | Google Cloud Run | Render | Heroku |
| :--- | :--- | :--- | :--- |
| **Web Service (Free Tier)** | **Very Generous:** <br> • 180,000 vCPU-sec/mo <br> • 360,000 GiB-sec/mo <br> • 2 million requests/mo | **Generous:** <br> • 750 instance hours/mo <br> • 100 GB bandwidth/mo | **No Free Tier:** <br> • Starts at **$5/mo**. |
| **Database (Free Tier)** | No perpetual free tier. | **Yes (Expires):** <br> • Free PostgreSQL. <br> • **Expires after 90 days.** | **No Free Tier:** <br> • Starts at **$5/mo**. |
| **Starting Price** | Potentially **$0** | Potentially **$0** (web service only) | **$10/mo** (web service + db) |

**Decision & Rationale:**

*   **Decision:** The project will use a **platform-agnostic, container-based (Docker) deployment strategy**. This ensures the application is portable and can be deployed consistently across different environments.
*   **Initial Target (Development/Testing):** The user's existing **Hetzner VPS** will be used for initial deployment and testing. This is ideal for GDPR as Hetzner is a German provider and avoids the complexity of signing Data Processing Addendums (DPAs) with US-based cloud providers.
*   **Long-Term Target (Production):** The **school's own server** is the preferred long-term solution to ensure project continuity. The containerized approach will facilitate this future migration.

### Phase 2: Containerization
*   [x] Create a `Dockerfile` for the FastAPI application.
*   [x] Ensure the Docker image includes all necessary dependencies and configurations.
*   [x] Build and test the Docker image locally.

### Phase 3: Configuration and Secrets Management
*   [x] Identify all environment-specific configurations (e.g., database connection strings, API keys).
*   [x] Implement a secure method for managing secrets in the production environment (e.g., environment variables, secret management services).

### Phase 4: CI/CD Pipeline Setup
*   [ ] Set up a CI/CD pipeline (e.g., GitHub Actions, GitLab CI, Jenkins) to automate:
    *   Building the Docker image on code push.
    *   Pushing the image to a container registry.
    *   Deploying the new image to the chosen platform.
*   [ ] Configure health checks and monitoring for the deployed backend.
