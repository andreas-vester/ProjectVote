#!/bin/sh

# This script is the container's entrypoint. It's a best practice for Docker
# containers that need to run as a non-root user but also need to write to
# a bind-mounted volume owned by a host user.

# 1. Set ownership of the data directory to the appuser.
#    This ensures that the application can write to the database file,
#    regardless of the host user's UID/GID.
chown -R appuser:appuser /app/data

# 2. Execute the main command (CMD) passed to the container.
#    `gosu` is a lightweight tool for dropping privileges.
#    This command runs the uvicorn server as the `appuser`.
exec gosu appuser "$@"
