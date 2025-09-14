FROM python:3.13-slim

# Build argument for service directory
ARG SERVICE_DIR=chat

# Create a non-root user, create their home directory, and set permissions
RUN groupadd -r appuser && useradd -m --no-log-init -r -g appuser appuser

# Set the working directory inside the container
WORKDIR /app

# Copy all necessary files and source code as the root user.
# The order of these COPY commands is important for build caching.
COPY ${SERVICE_DIR}/pyproject.toml .
COPY ${SERVICE_DIR}/uv.lock .
COPY ${SERVICE_DIR}/run.sh .
COPY static ./static
COPY ${SERVICE_DIR}/. .

# Change ownership of the /app directory and its contents to appuser.
# Also change ownership of the home directory to appuser.
RUN chown -R appuser:appuser /app /home/appuser

# Switch to the non-root user for all subsequent commands.
USER appuser

# Create a virtual environment and install dependencies in a single RUN command.
RUN python -m venv .venv && \
    ./.venv/bin/pip install uv && \
    ./.venv/bin/uv sync && \
    chmod +x run.sh

# Expose the application port
EXPOSE 8080

# The container will start by running the executable script as the appuser.
ENTRYPOINT ["./run.sh"]