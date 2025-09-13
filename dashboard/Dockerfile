FROM python:3.13-slim

# Build argument for service directory
ARG SERVICE_DIR=dashboard

# Create a non-root user and group
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files and run.sh as root
COPY ${SERVICE_DIR}/pyproject.toml .
COPY ${SERVICE_DIR}/uv.lock .
COPY ${SERVICE_DIR}/run.sh .

# Make the run.sh script executable while still running as root
RUN chmod +x run.sh

# Switch to the non-root user for security
USER appuser

# Install uv and sync dependencies as the new user.
RUN pip install uv
RUN uv sync

# Copy the static folder from the build context (root/static)
COPY static ./static

# Copy the service-specific application code
COPY ${SERVICE_DIR}/. .

# Expose the application port
EXPOSE 8080

# Set the entrypoint to the run.sh script
ENTRYPOINT ["./run.sh"]