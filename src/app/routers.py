from fastapi import FastAPI
from modules.V1.V1routers import router as v1_router

def routers(app: FastAPI):
    app.include_router(v1_router, prefix="/api/v1", tags=["V1"])
