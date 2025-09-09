# Stage 1: Build dependencies using the official astral/uv image
# This image contains Python 3.13 and uv pre-installed.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Set the working directory
WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment at /app/.venv
RUN uv sync


# Stage 2: Create the final, clean runtime image
FROM python:3.13-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY src/ ./src/

# Add the virtual environment's executables to the PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src

# Create a non-root user for security
RUN useradd --create-home appuser

# Create and set permissions for the data directory
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

USER appuser

# Expose the port the app will run on
EXPOSE 8008

# Command to run the application
CMD ["uvicorn", "projectvote.backend.main:app", "--host", "0.0.0.0", "--port", "8008"]
