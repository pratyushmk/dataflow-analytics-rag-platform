# Operational Guide

## Local Development

The system uses LocalStack to simulate AWS services locally.  
S3 is accessed via the LocalStack endpoint at http://localhost:4566.

## Required Services

- LocalStack (S3)
- Apache Spark
- FastAPI
- FAISS vector store

## Startup Order

1. Start LocalStack
2. Upload sample raw events to the raw S3 bucket
3. Run the Spark ETL job
4. Build the RAG index
5. Start the FastAPI server

## RAG Index Maintenance

The RAG index is built offline using documentation stored in the `docs/` directory.
Whenever documentation changes, the index must be rebuilt by running the build_index script.

## Troubleshooting

- If analytics endpoints return empty results, ensure the ETL job has completed successfully
- If RAG responses seem outdated, rebuild the FAISS index
- Ensure AWS credentials are configured when running locally
