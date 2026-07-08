from fastapi import FastAPI
from app.api.v1.endpoints.vehicles import router as vehicles_router

app = FastAPI()

app.include_router(vehicles_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}