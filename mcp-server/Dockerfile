FROM python:3.13-slim

# Build argument for service directory
ARG SERVICE_DIR=mcp-server

# Create a non-root user and group
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files first to leverage Docker's build cache
COPY ${SERVICE_DIR}/pyproject.toml .
COPY ${SERVICE_DIR}/uv.lock .

# Install uv and sync dependencies. This step is cached.
RUN pip install uv
RUN uv sync

# Copy the static folder from the build context (root/static)
COPY static ./static

# Copy the service-specific application code
COPY ${SERVICE_DIR}/. .

# Expose the application port
EXPOSE 8080

# Define the command to run the application
CMD ["uv", "run", "server.py"]