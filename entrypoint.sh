#!/bin/sh

# This script is the container's entrypoint. It's a best practice for Docker
# containers that need to run as a non-root user but also need to write to
# a bind-mounted volume owned by a host user.

# 1. Set ownership of the data directory to the appuser.
#    This ensures that the application can write to the database file,
#    regardless of the host user's UID/GID.
chown -R appuser:appuser /app/data

# 2. Run database migrations before starting the application.
#    This ensures the database schema is up-to-date with the current code.
#    Migrations are run as root first (before dropping privileges) to ensure
#    permissions are correct.
echo "Running database migrations..."
alembic -c alembic.ini upgrade head
if [ $? -ne 0 ]; then
    echo "Failed to run database migrations" >&2
    exit 1
fi
echo "Database migrations completed successfully"

# 3. Execute the main command (CMD) passed to the container.
#    `gosu` is a lightweight tool for dropping privileges.
#    This command runs the uvicorn server as the `appuser`.
exec gosu appuser "$@"
