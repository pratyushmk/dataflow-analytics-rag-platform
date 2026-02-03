FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -U pip && pip install .

COPY api/ api/
COPY rag/ rag/

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]