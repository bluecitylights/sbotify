# Use a Python 3.13 slim image for a lightweight base.
FROM python:3.13-slim

# Set the working directory inside the container.
WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

# Install the dependencies from the shared lock file.
RUN pip install uv
RUN uv sync

COPY . .
# Expose the port that the FastAPI server will run on.
EXPOSE 8000

CMD ["uv", "run", "server.py"]
