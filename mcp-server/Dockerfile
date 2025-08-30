# Use a Python 3.13 slim image for a lightweight base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# This means the uv sync step will only run if dependencies change
COPY ./pyproject.toml ./uv.lock ./

# Install uv and then sync the dependencies
RUN pip install uv && uv sync

# Copy the rest of the application code
COPY . .

# Expose the port that the fastmcp server will run on
EXPOSE 8000

# Command to run the application using uv
# --host 0.0.0.0 is crucial for making the app accessible outside the container
CMD ["uv", "run", "--host", "0.0.0.0", "server.py"]
