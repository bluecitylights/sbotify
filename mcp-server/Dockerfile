FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv
RUN uv sync

COPY . .

EXPOSE 8080

CMD ["uv", "run", "server.py"]
