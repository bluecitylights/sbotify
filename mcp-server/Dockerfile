# Use a Python 3.13 slim image for a lightweight base.
FROM python:3.13-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the contents of the build context (which is ./mcp-server)
# into the /app directory inside the container.
COPY . .

# Install the necessary Python dependencies.
RUN pip install fastmcp uvicorn

# Expose the port that the fastmcp server will run on.
EXPOSE 8000

# The command to run the application using uvicorn.
# `server:mcp` tells uvicorn to look for a file named `server.py` and an application
# instance named `mcp` inside it.
CMD ["uvicorn", "server:mcp", "--host", "0.0.0.0", "--port", "8000"]
