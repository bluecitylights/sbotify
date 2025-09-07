FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files first to leverage Docker's build cache
COPY pyproject.toml .
COPY uv.lock .

# Install uv and sync dependencies. This step is cached.
RUN pip install uv
RUN uv sync

# Copy the rest of your application code
COPY . .

# Copy the shared static assets from the parent directory.
# The build context is 'chat', so '..' refers to the project root.
COPY ../static /app/static

# Expose the application port
EXPOSE 8080

# Make the script executable
RUN chmod +x run.sh
ENTRYPOINT ["./run.sh"]
