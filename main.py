from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .database import db
from .services.engine import service

app = FastAPI(title="Sinhala Storytelling API")

# DB Connection & Seeding
@app.on_event("startup")
async def startup_event():
    db.connect()
    await service.seed_data()

@app.on_event("shutdown")
async def shutdown_event():
    db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Sinhala Storytelling API"}
