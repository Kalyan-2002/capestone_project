
FROM python:3.11-slim

# Environment

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Required graded baseline
ENV MOCK_LLM=1

# Working directory

WORKDIR /app

# System dependencies

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project

COPY . /app

# Install Python dependencies

RUN pip install --no-cache-dir \
    -r requirements.txt

# Build ChromaDB during image creation

RUN python -m support_assistant.ingest

# API port

EXPOSE 7860

# Start FastAPI


CMD [
    "uvicorn",
    "support_assistant.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "7860"
]
