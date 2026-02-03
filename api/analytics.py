import pandas as pd
from fastapi import APIRouter, HTTPException

from utils.get_s3_fs import get_s3_fs

router = APIRouter()

@router.get("/events")
def event_summary(event_type: str):
    fs = get_s3_fs()

    base_path = f"dataflow-processed/events/event_type={event_type}"

    # 🔥 Explicitly list parquet files
    files = fs.glob(f"{base_path}/*.parquet")

    if not files:
        return {"error": "Analytics not ready. Run ETL first."}

    try:
        df = pd.read_parquet(files, filesystem=fs)
    except Exception as e:
        # TEMPORARY: expose the real error
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "event_type": event_type,
        "total_events": int(df["event_count"].sum())
    }
