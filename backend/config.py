"""
Application configuration.
All settings are loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "supply_chain.db"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# ---------------------------------------------------------------------------
# CORS — allow the Vite dev server during development
# ---------------------------------------------------------------------------
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
).split(",")

# ---------------------------------------------------------------------------
# n8n
# ---------------------------------------------------------------------------
N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")

# ---------------------------------------------------------------------------
# External API keys (Phase 2+)
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
