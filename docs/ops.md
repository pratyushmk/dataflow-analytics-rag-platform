# Operational Guide

This document describes runtime behavior, operational considerations, and recovery procedures for the DataFlow Analytics & RAG Platform.

It is intended for operators and maintainers, not first-time users.
For setup and usage instructions, see `README.md`

---

## Execution Modes

This project supports two execution modes:

### Local Spark ETL

- Spark runs on the host machine
- Requires Java 17 (Spark 4.x requirement)
- Connects to LocalStack via http://localhost:4566
- AWS credentials must be exported in the shell

Spark ETL assumes infrastructure already exists and acts strictly as a client.

### Containerized API

- FastAPI and RAG run inside Docker
- LocalStack runs as a Docker service
- Analytics endpoint(s3) connects to LocalStack via http://localstack:4566
- Credentials and endpoints are injected via environment variables
  > Inside Docker, `localhost` refers to the container itself and must never be used to reach LocalStack.

---

## Required Services

- LocalStack (S3-compatible storage)
- Apache Spark 4.x (requires Java 17)
- FastAPI (analytics and RAG API)
- FAISS vector store (RAG index)

---

## Startup Order

Infrastructure must be started before compute workloads.

Recommended order:

1. Start LocalStack
2. Upload sample raw events to the raw S3 bucket
3. Run the Spark ETL job
4. Build the RAG index
5. Start the FastAPI server

Spark ETL assumes that LocalStack and S3 buckets already exist and does not manage infrastructure lifecycle.

---

## Environment Variables

The following environment variables are required at runtime:

| Variable                | Used By    | Required    | Notes                       |
| ----------------------- | ---------- | ----------- | --------------------------- |
| `OPENAI_API_KEY`        | API        | Yes         | Not committed               |
| `AWS_ACCESS_KEY_ID`     | Spark, API | Yes         | Dummy values for LocalStack |
| `AWS_SECRET_ACCESS_KEY` | Spark, API | Yes         | Dummy values for LocalStack |
| `AWS_DEFAULT_REGION`    | Spark, API | Yes         | Typically `us-east-1`       |
| `AWS_ENDPOINT_URL`      | API        | Docker only | `http://localstack:4566`    |

Spark ETL relies on the AWS default credential provider chain, which requires credentials to be exported in the shell.

---

## Stateful Artifacts

### Processed Analytics Data

- Stored in S3 as partitioned Parquet
- Written by Spark ETL
- Read by the Analytics API

### ETL Checkpoint

- Stored in S3
- Tracks last processed timestamp
- Enables incremental ETL
- Must be deleted to force a full reprocess

### FAISS RAG Index

- Generated offline from files in `docs/`
- Stored locally under `rag/index/`
- Not committed to Git
- Must be rebuilt when documentation changes
- Mounted into the API container at runtime

Loss of any artifact requires regeneration via ETL or index rebuild.

---

## RAG Index Maintenance

- Documentation lives in `docs/`
- The index is built using the `build_index` script
- The index must be rebuilt whenever documentation changes
- The API assumes the index exists at startup
- When running in Docker, the index is mounted into the API container as a volume

If the index is missing, RAG endpoints will fail.

---

## Common Failures and Recovery

### Spark fails with `UnsupportedClassVersionError`

- Cause: Java version mismatch
- Fix: Ensure Java 17 is active

### Spark cannot find S3 path

- Cause: No objects under S3 prefix
- Fix: Upload at least one file under the prefix

### Spark cannot load AWS credentials

- Cause: Credentials not exported in shell
- Fix: Export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### Analytics API cannot connect to S3

- Cause: Using `localhost` inside Docker
- Fix: Use `AWS_ENDPOINT_URL=http://localstack:4566`

### Analytics endpoint returns "Analytics not ready

- Cause: ETL has not been run
- Fix: Run Spark ETL successfully

### RAG responses are outdated

- Cause: FAISS index not rebuilt after doc changes
- Fix: Re-run the index build script

---

## Design Notes

- Infrastructure and compute are intentionally decoupled
- Spark ETL is designed to be idempotent and safely re-runnable
- LocalStack is used only for local development; no code changes are required to switch to real AWS S3
- Secrets are injected at runtime and never stored in code or images

---

## Scope of This Document

This file intentionally excludes:

- Setup instructions
- Code-level details
- Architecture diagrams

Those are documented in `README.md` and inline code comments.

---
