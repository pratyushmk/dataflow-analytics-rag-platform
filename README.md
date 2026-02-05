# DataFlow Analytics RAG Platform

A cloud-native event analytics platform that combines **Spark-based ETL**, **FastAPI analytics APIs**, and a **RAG (Retrieval-Augmented Generation) system** for answering operational and business questions using internal documentation.

---

## Quick Start

```bash
git clone <repo>

# Creates venv and installs dependencies
poetry install

# Put your actual OPENAI_API_KEY
export OPENAI_API_KEY=<your_api_key> sk----

docker compose up -d

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

aws --endpoint-url=http://localhost:4566 s3 mb s3://dataflow-raw
aws --endpoint-url=http://localhost:4566 s3 mb s3://dataflow-processed
aws --endpoint-url=http://localhost:4566 \
  s3 cp sample_events.json \
  s3://dataflow-raw/events/sample_events.json

spark-submit \
--packages org.apache.hadoop:hadoop-aws:3.4.0 \
etl/process_events.py
```

---

## Features

- **Event Ingestion & ETL**
  - Apache Spark ETL processes raw customer interaction events
  - Incremental processing using timestamp-based checkpoints
  - Aggregated, partitioned Parquet output stored in S3

- **Analytics API**
  - FastAPI service exposing aggregated metrics
  - Reads partitioned Parquet directly from S3
  - Designed for local development with LocalStack

- **RAG (Retrieval-Augmented Generation)**
  - FAISS vector index built from system documentation
  - Semantic search over internal docs
  - LLM answers grounded strictly in retrieved context

- **Local-First, Cloud-Ready**
  - LocalStack used for S3 emulation
  - Same architecture works against real AWS S3 in production

---

## Architecture Overview

```text
                +----------------------+
                |   Docs (*.md)        |
                |  ETL / Ops / API     |
                +----------+-----------+
                           |
                     Build FAISS Index
                           |
                +----------v-----------+
                |     FAISS Index      |
                +----------+-----------+
                           |
        +------------------+------------------+
        |                                     |
+-------v--------+                    +-------v--------+
|  FastAPI       |                    |  FastAPI       |
|  RAG Search    |                    |  Analytics API |
+-------+--------+                    +-------+--------+
        |                                     |
        |                                     |
        |                          +----------v----------+
        |                          |  Processed S3       |
        |                          |  Parquet (by type)  |
        |                          +----------+----------+
        |                                     ^
        |                                     |
        |                          +----------+----------+
        |                          |  Spark ETL Job      |
        |                          |  (Incremental)     |
        |                          +----------+----------+
        |                                     ^
        |                                     |
        |                          +----------+----------+
        |                          |  Raw S3 Events      |
        |                          |  NDJSON             |
        |                          +---------------------+

```

## Tech Stack

- **Apache Spark** – batch ETL and aggregation
- **FastAPI** – REST APIs
- **FAISS** – vector similarity search
- **LangChain** – RAG orchestration
- **OpenAI Embeddings** – semantic embeddings
- **Pandas / PyArrow** – analytics reads
- **LocalStack** – local AWS S3 emulation
- **AWS S3** – raw + processed storage

---

## Running the Project

This project supports two execution modes:

- Containerized execution using Docker Compose (recommended for API + LocalStack)
- Local execution on your machine (recommended for Spark ETL)

Both modes use the same architecture and codebase.

---

## Option 1: Run Using Docker Compose (API + LocalStack)

This mode is recommended for running the FastAPI analytics and RAG services together with LocalStack.

### Build and start containers

```bash
docker compose up --build
```

This starts:

- LocalStack (S3)
- FastAPI service (analytics + RAG)

### Environment Variables

Docker Compose injects the required environment variables:

```bash
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localstack:4566
OPENAI_API_KEY=your_api_key
```

The OpenAI API key is never committed and should be provided via:

- shell export, or
- local .env file

### FAISS Index (RAG)

The FAISS vector index is a generated artifact and is not committed to Git.

Build the RAG index when a new doc is created or an existing doc is updated.

```bash
export OPENAI_API_KEY=<your_api_key> sk----

python rag/build_index.py
```

Docker Compose mounts the index into the container:

```bash
volumes:
  - ./rag/index:/app/rag/index
```

## Option 2: Run Locally on Your Machine (Spark ETL)

> LocalStack must be running before executing the Spark ETL job.

This mode is ideal for running the Spark ETL, since Spark requires Java and is often easier to debug outside containers.

### Prerequisites

- Python `3.11 (recommended)`
- Java 17+
- Apache Spark 4.x
- LocalStack
- AWS CLI

---

### Create S3 Buckets

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://dataflow-raw
aws --endpoint-url=http://localhost:4566 s3 mb s3://dataflow-processed
```

### Upload Sample Events

Raw events must be line-delimited JSON (NDJSON), not a JSON array.

```bash
aws --endpoint-url=http://localhost:4566 \
  s3 cp sample_events.json \
  s3://dataflow-raw/events/sample_events.json
```

### Export AWS Credentials (Required for Spark)

```bash
  export AWS_ACCESS_KEY_ID=test
  export AWS_SECRET_ACCESS_KEY=test
  export AWS_DEFAULT_REGION=us-east-1
  export AWS_EC2_METADATA_DISABLED=true
```

### Run Spark ETL

```bash
spark-submit \
--packages org.apache.hadoop:hadoop-aws:3.4.0 \
etl/process_events.py
```

Spark connects to LocalStack using:

```bash
http://localhost:4566
```

and writes partitioned Parquet output to the processed bucket.

---

## Troubleshooting

If you encounter issues during setup:

- Ensure LocalStack is running before executing the Spark ETL
- Spark requires **Java 17** (Spark 4.x)
- At least one object must exist under an S3 prefix before Spark can read it
- When running inside Docker, services must use `http://localstack:4566`, not `localhost`

For detailed operational guidance and recovery steps, see [`ops.md`](./ops.md).

---

## Analytics API Usage

### Endpoint

```sql
GET /analytics/events?event_type=<type>
```

### Example

```bash
curl "http://127.0.0.1:8000/analytics/events?event_type=click"
```

### Response

```json
{
  "event_type": "click",
  "total_events": 42
}
```

---

## RAG API Usage

### Endpoint

```sql
GET /rag/search?query=<question>
```

### Example

```bash
curl "http://127.0.0.1:8000/rag/search?query=How does the ETL process click events?"
```

### Response

```json
{
  "query": "How does the ETL process click events?",
  "answer": "Click events are ingested from the raw S3 bucket, processed by a Spark ETL job, aggregated by event_type, and written as partitioned Parquet files.",
  "sources": ["etl.md"]
}
```

---

## Incremental ETL Design

- ETL maintains a checkpoint timestamp in S3
- Only events newer than the checkpoint are processed
- First run performs a full load
- Safe to re-run without duplication

---

## Design Principles

- Clear separation of ETL, analytics, and RAG
- Derived artifacts (FAISS index) are not committed
- Local-first development, cloud-ready architecture
