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

# Expose the application port
EXPOSE 8080

# Define the command to run the application
CMD ["uvicorn", "chat.src.main:app", "--host", "0.0.0.0", "--port", "8000"]