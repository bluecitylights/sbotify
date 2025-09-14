FROM python:3.13-slim

# Build argument for service directory
ARG SERVICE_DIR=chat

# Create a non-root user and group, and create their home directory
RUN groupadd -r appuser && useradd -m --no-log-init -r -g appuser appuser

# Set the working directory inside the container
WORKDIR /app

# Copy all necessary files and source code as the root user.
# This prevents permission issues from the host machine.
COPY ${SERVICE_DIR}/pyproject.toml .
COPY ${SERVICE_DIR}/uv.lock .
COPY ${SERVICE_DIR}/run.sh .
COPY static ./static
COPY ${SERVICE_DIR}/. .

# Change ownership of the app directory and its contents to appuser.
# This is a critical step for security and permissions.
RUN chown -R appuser:appuser /app

# Change ownership of the appuser's home directory to appuser
# This prevents issues with caches
RUN chown -R appuser:appuser /home/appuser

# Switch to the non-root user for all subsequent commands.
USER appuser

# Create a virtual environment as the non-root user
RUN python -m venv .venv

# Install uv into the virtual environment using its own pip executable.
RUN ./.venv/bin/pip install uv

# Use uv to sync the remaining dependencies from uv.lock.
RUN ./.venv/bin/uv sync

# Make the run.sh script executable. This will now succeed.
RUN chmod +x run.sh

# Expose the application port
EXPOSE 8080

# The container will start by running the executable script as the appuser.
ENTRYPOINT ["./run.sh"]