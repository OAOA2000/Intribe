import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("BASE_URL", os.getenv("LLM_BASE_URL", "")).strip()
    LLM_MODEL_NAME = os.getenv("MODEL_NAME", os.getenv("LLM_MODEL_NAME", "")).strip().strip("'\"")
    LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", os.getenv("REQUEST_TIMEOUT_SECONDS", "15")))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))

    JSON_AS_ASCII = False
