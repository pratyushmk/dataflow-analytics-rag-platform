import sys
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, count, col, window, lit, max as spark_max

shared_dir = Path(__file__).resolve().parent.parent / "shared"
sys.path.append(str(shared_dir))

import s3_client

RAW_PATH = "s3a://dataflow-raw/events/"
PROCESSED_PATH = "s3a://dataflow-processed/events/"
CHECKPOINT_KEY = "checkpoints/last_processed_ts.txt"
BUCKET = "dataflow-processed"

spark = (
    SparkSession.builder
    .appName("customer-events-process-etl")
    .config("spark.sql.shuffle.partitions", "4")

    # 🔑 LocalStack S3 settings (MANDATORY)
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:4566")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

    .getOrCreate()
)

# ---------- Read last checkpoint ----------

s3 = s3_client.get_s3_client()

last_ts = None
try:
    obj = s3.get_object(Bucket=BUCKET, Key=CHECKPOINT_KEY)
    last_ts = obj["Body"].read().decode("utf-8").strip()
    print(f"Last processed timestamp:{last_ts}")
except s3.exceptions.NoSuchKey:
    print("No checkpoint found. Full load.")

# ---------- Read raw events ----------

df = spark.read.json(RAW_PATH)

cleaned_df = (
    df
    .withColumn("event_ts", to_timestamp("timestamp")).dropna(subset=['user_id', 'event_type', 'event_ts'])

)

# ---------- Filter only new events ----------
if last_ts:
    cleaned_df = cleaned_df.filter(
        col("event_ts") > to_timestamp(lit(last_ts))
    )

if cleaned_df.rdd.isEmpty():
    print("No new events to process. Exiting.")
    spark.stop()
    exit(0)

# ---------- Aggregate ----------
aggregated = (
    cleaned_df
    .groupBy(
        window("event_ts", "1 Hour"), 
        col("event_type")
        )
        .agg(
            count("*").alias("event_count")
            )
)

# ---------- Write output ----------

(
    aggregated
    .write
    .mode("append")
    .partitionBy("event_type")
    .parquet(PROCESSED_PATH)
)

# ---------- Update checkpoint ----------
max_ts = cleaned_df.select(spark_max("event_ts")).collect()[0][0]

s3.put_object(
    Bucket=BUCKET,
    Key=CHECKPOINT_KEY,
    Body=max_ts.isoformat()
)

print("Updated checkpoint to:", max_ts)

spark.stop()