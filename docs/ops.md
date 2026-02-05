# Operational Guide

## Local Development

The system uses LocalStack to simulate AWS services locally.

- When running Spark ETL on the host machine, S3 is accessed via:
  http://localhost:4566
- When running the FastAPI service inside Docker, S3 is accessed via:
  http://localstack:4566

The correct endpoint is injected via environment variables.

## Required Services

- LocalStack (S3-compatible storage)
- Apache Spark 4.x (requires Java 17)
- FastAPI (analytics and RAG API)
- FAISS vector store (RAG index)

## Startup Order

1. Start LocalStack
2. Upload sample raw events to the raw S3 bucket
3. Run the Spark ETL job
4. Build the RAG index
5. Start the FastAPI server

Spark ETL assumes that LocalStack and S3 buckets already exist and does not manage infrastructure lifecycle.

## RAG Index Maintenance

The RAG index is built offline using documentation stored in the `docs/` directory.

- The FAISS index is a generated artifact and is not committed to Git
- The index must be rebuilt whenever documentation changes
- When running in Docker, the index is mounted into the API container as a volume

## Troubleshooting

### Common Issues

**Spark fails with UnsupportedClassVersionError**

- Cause: Java version mismatch
- Fix: Ensure Java 17 is active

**Spark cannot find S3 path**

- Cause: No objects exist under the S3 prefix
- Fix: Upload at least one file under the prefix (S3 has no real directories)

**Analytics API cannot connect to S3**

- Cause: Using `localhost` inside Docker
- Fix: Ensure `AWS_ENDPOINT_URL=http://localstack:4566` is set

**Analytics endpoint returns "Analytics not ready"**

- Cause: ETL has not been run
- Fix: Run Spark ETL successfully

**RAG responses are outdated**

- Cause: FAISS index not rebuilt after doc changes
- Fix: Re-run the index build script
