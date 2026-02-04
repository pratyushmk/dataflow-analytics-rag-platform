FROM python:3.11-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (minimal, safe)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency metadata only (better caching)
COPY pyproject.toml ./

# Install dependencies ONLY (no project install)
RUN pip install --no-cache-dir -U pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY api/ api/
COPY shared/ shared
COPY utils/ utils
COPY rag/ rag/
COPY docs/ docs/

# Expose API port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
