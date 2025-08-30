# Use the official Python base image
FROM python:3.12-bullseye

# Set the working directory in the container
WORKDIR /app

# Install uv and the FastMCP library
RUN pip install uv && uv pip install fastmcp

# Copy the application code into the container
COPY . /app
