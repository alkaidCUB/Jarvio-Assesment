from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app import models
from app.routers import auth, workflows, products

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Workflow Builder API",
    description="A simple workflow builder API for take-home interviews",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workflows.router)
app.include_router(products.router)


@app.get("/")
def read_root():
    return {"message": "Workflow Builder API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}