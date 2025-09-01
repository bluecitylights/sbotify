# Use a Python 3.13 slim image for a lightweight base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app/mcp-client

# Copy the dependency files from the project root.
# Docker's build context is set to the project root in docker-compose.yml.
COPY pyproject.toml ./
COPY uv.lock ./

COPY ./mcp-client .

# Install uv first, then use it to sync the dependencies
RUN pip install uv
RUN uv sync

# Copy the client's source code into the container
# The `.` at the end means "copy all files from the current build context to the destination"
COPY . .
