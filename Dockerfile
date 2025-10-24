# Stage 1: Build dependencies using the official astral/uv image
# This image contains Python 3.13 and uv pre-installed.
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder

# Set the working directory
WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment at /app/.venv
RUN uv sync


# Stage 2: Create the final, clean runtime image
FROM python:3.14-slim-trixie

# Set the working directory
WORKDIR /app

# Install gosu for privilege-dropping. This allows the container to start as root
# to fix permissions and then drop to a non-root user to run the application.
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends wget; \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/1.17/gosu-$(dpkg --print-architecture | awk -F- '{print $NF}')"; \
    chmod +x /usr/local/bin/gosu; \
    # Verify that gosu is installed and works
    gosu --version; \
    # Clean up
    apt-get purge -y --auto-remove wget; \
    rm -rf /var/lib/apt/lists/*;

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY src/ ./src/

# Add the virtual environment's executables to the PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src

# Create a non-root user for security
RUN useradd --create-home appuser

# Copy and set up the entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint to our script. This script will fix permissions and then
# use gosu to run the main command (CMD) as the non-root 'appuser'.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Expose the port the app will run on
EXPOSE 8008

# Command to run the application. This will be executed by the entrypoint script.
CMD ["uvicorn", "projectvote.backend.main:app", "--host", "0.0.0.0", "--port", "8008"]
