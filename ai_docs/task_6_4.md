# Task 6.4: Database Migrations (Alembic)

## Goal
Implement a robust database migration system using Alembic to manage schema changes, ensuring smooth upgrades and downgrades for the application's database.

## Plan
1.  Integrate Alembic into the project.
2.  Configure Alembic to work with SQLAlchemy models.
3.  Generate and apply initial migration script.
4.  Define a process for creating and applying future migrations.
5.  Automate migration application in the Docker container startup.

## Tasks

### Phase 1: Alembic Integration and Configuration
Refer to the latest `alembic` documentation at https://alembic.sqlalchemy.org/en/latest/index.html
*   [x] Add `alembic` to `pyproject.toml` dependencies.
*   [x] Initialize Alembic environment in the project root (`uv run alembic init --template async --template pyproject alembic`).
*   [x] Configure `alembic.ini` to point to the correct database URL and SQLAlchemy models.
*   [x] Modify `migrations/env.py` to import the base metadata from `src/projectvote/backend/models.py`.

### Phase 2: Initial Migration Creation and Application
*   [x] Generate the first migration script to reflect database schema changes:
    * Added columns to table ``applications``.
      1. ``created_at = Column(DateTime, nullable=False, server_default=func.now())``
      2. ``concluded_at = Column(DateTime, nullable=True)``
    * Added columns to table ``votes``.
      1. ``voted_at = Column(DateTime, nullable=True)``
*   [x] Manually inspect and adjust the generated migration script to include default values for non-nullable columns being added to existing data (e.g., `created_at`).
*   [x] Apply the migration to the development database (`alembic upgrade head`).

### Phase 3: Docker Integration
*   [x] Update the Dockerfile or `entrypoint.sh` to automatically run `alembic upgrade head` during container startup to apply any pending migrations.
*   [x] Ensure the migration step runs before the application server starts.

### Verification
*   [x] After applying migrations, verify that the database schema is updated correctly.
*   [x] Test the application with the migrated database to ensure data integrity and functionality.
