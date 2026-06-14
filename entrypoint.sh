#!/bin/sh

# This script is the container's entrypoint. It's a best practice for Docker
# containers that need to run as a non-root user but also need to write to
# a bind-mounted volume owned by a host user.

# 1. Run database migrations before starting the application.
#    This ensures the database schema is up-to-date with the current code.
#    Migrations are run as root first (before dropping privileges).
#    This must run BEFORE chown so that any new files created during migration
#    (e.g., applications.db) are also included in the ownership change.
echo "Running database migrations..."
alembic -c alembic.ini upgrade head
if [ $? -ne 0 ]; then
    echo "Failed to run database migrations" >&2
    exit 1
fi
echo "Database migrations completed successfully"

# 2. Set ownership of the data directory to the appuser.
#    This ensures that all files (including newly created DB during migration)
#    are writable by the application.
chown -R appuser:appuser /app/data

# 3. Execute the main command (CMD) passed to the container.
#    `gosu` is a lightweight tool for dropping privileges.
#    This command runs the uvicorn server as the `appuser`.
exec gosu appuser "$@"
