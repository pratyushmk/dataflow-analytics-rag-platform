from fastapi import FastAPI
from api.analytics import router as analytics_router
from api.rag import router as rag_router

app = FastAPI(title="DataFlow Analytics API")

app.include_router(analytics_router, prefix="/analytics")
app.include_router(rag_router, prefix="/rag")
