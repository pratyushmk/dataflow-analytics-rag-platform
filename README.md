# DataFlow Analytics RAG Platform

A cloud-native event analytics platform that combines **Spark-based ETL**, **FastAPI analytics APIs**, and a **RAG (Retrieval-Augmented Generation) system** for answering operational and business questions using internal documentation.

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
        |                          |  JSON             |
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

## Local Development Setup

### Prerequisites

- Python `3.11 – 3.14`
- Java 17+
- Apache Spark 4.x
- LocalStack
- AWS CLI

---

### Start LocalStack

```bash
localstack start
```

### Create S3 Buckets

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://dataflow-raw
aws --endpoint-url=http://localhost:4566 s3 mb s3://dataflow-processed
```

### Upload Sample Events

```bash
aws --endpoint-url=http://localhost:4566 \
  s3 cp sample_events.json \
  s3://dataflow-raw/events/sample_events.json
```

### Run Spark ETL

```bash
spark-submit etl/process_events.py
```

### Build the RAG index

```bash
export OPENAI_API_KEY=your_api_key
python rag/build_index.py
```

### Start the API

```bash
uvicorn api.main:app --reload
```

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

## Incremental ETL Design

- ETL maintains a checkpoint timestamp in S3
- Only events newer than the checkpoint are processed
- First run performs a full load
- Safe to re-run without duplication

## Design Principles

- Design Principles
- Clear separation of ETL, analytics, and RAG
- Derived artifacts (FAISS index) are not committed
- Local-first development, cloud-ready architecture
