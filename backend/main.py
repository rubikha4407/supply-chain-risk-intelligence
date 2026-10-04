"""
Supply Chain Risk Intelligence & Recovery Orchestrator — FastAPI Backend

Entry point: uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from database import engine, SessionLocal, Base

# Import all models so Base.metadata knows about every table
import models  # noqa: F401

from routers import suppliers, events, risk, recovery, simulation, n8n
from seed.seed_data import seed_database


# ---------------------------------------------------------------------------
# Lifespan — runs on startup and shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed demo data on startup."""
    print("🚀 Starting Supply Chain Risk Intelligence backend...")
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created.")

    print("🌱 Loading seed data...")
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    yield  # App runs here

    print("👋 Shutting down.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Supply Chain Risk Intelligence",
    description=(
        "AI-powered supply chain risk detection, impact analysis, "
        "and recovery orchestration platform."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(suppliers.router)
app.include_router(events.router)
app.include_router(risk.router)
app.include_router(recovery.router)
app.include_router(simulation.router)
app.include_router(n8n.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Supply Chain Risk Intelligence",
        "version": "0.1.0",
    }
