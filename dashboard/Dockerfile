FROM python:3.13-slim

# Build argument for service directory
ARG SERVICE_DIR=dashboard

# Create a non-root user and group, and create their home directory
RUN groupadd -r appuser && useradd -m --no-log-init -r -g appuser appuser

# Set the working directory inside the container
WORKDIR /app

# Copy all necessary files and source code.
COPY ${SERVICE_DIR}/pyproject.toml .
COPY ${SERVICE_DIR}/uv.lock .
COPY ${SERVICE_DIR}/run.sh .
COPY static ./static
COPY ${SERVICE_DIR}/. .

# Change ownership of the app directory and its contents to appuser.
# Also change ownership of the home directory to appuser.
RUN chown -R appuser:appuser /app /home/appuser

# Switch to the non-root user for all subsequent commands.
USER appuser

# Step 1: Create the virtual environment in its own command.
RUN python -m venv .venv

# Step 2: Install dependencies in a separate command.
RUN ./.venv/bin/pip install uv

# Step 3: Sync dependencies and make the run script executable.
RUN ./.venv/bin/uv sync && chmod +x run.sh

# Expose the application port
EXPOSE 8080

# The container will start by running the executable script as the appuser.
ENTRYPOINT ["./run.sh"]