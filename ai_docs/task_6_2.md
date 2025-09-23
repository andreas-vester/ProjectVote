# Task 6.2: Database Setup & Management

## Goal
Establish a robust and maintainable database setup for both development and production environments, integrated with the Docker setup.

## Plan
1.  Configure the database for the Docker environment.
2.  Define a backup and recovery strategy.
3.  Plan for future database migrations.

## Tasks

### Phase 1: Database Configuration in Docker
*   [x] Use SQLite for lightweight local development.
*   [x] Configure a Docker volume in `docker-compose.yml` to persist the SQLite database file (`data/applications.db`) across container restarts.
*   [x] Document the process for connecting to the database within the Docker environment.

### Phase 2: Backup and Recovery Strategy
*   [ ] For SQLite: The backup strategy is to simply back up the database file from the Docker volume.
*   [ ] Establish and document a recovery plan.

### Phase 3: Database Migrations
*   [ ] Choose and configure a database migration tool (e.g., Alembic for SQLAlchemy).
*   [ ] Define a process for managing schema changes as the application evolves.
*   [ ] Create initial migration scripts to version the database schema.
