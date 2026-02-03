# Event Processing ETL

## Overview

The Event Processing ETL ingests raw customer interaction events from an S3 bucket and transforms them into aggregated analytics data.

## Raw Events

Raw events are stored in the `dataflow-raw` S3 bucket under the `events/` prefix.  
Each event is stored as a single line JSON object and includes:

- event_id
- user_id
- event_type
- timestamp

## Processing Logic

The ETL job is implemented using Apache Spark. It performs the following steps:

1. Reads raw JSON events from S3
2. Parses timestamps into Spark timestamp format
3. Filters invalid or incomplete records
4. Aggregates events by event_type
5. Writes the aggregated results as partitioned Parquet files

## Output

Processed data is written to the `dataflow-processed` S3 bucket and partitioned by event_type:

- events/event_type=click/
- events/event_type=view/
- events/event_type=purchase/

## Incremental Processing

The ETL supports incremental processing by tracking the latest processed event timestamp in a checkpoint file stored in S3. Only events newer than the checkpoint timestamp are processed in subsequent runs.
