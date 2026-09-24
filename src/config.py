"""
Configuration module for the AI-Based Donation Management System.
Safely retrieves configuration from Streamlit secrets (st.secrets) or environment variables.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "Backend"
MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
DONOR_PICS_DIR = MEDIA_DIR / "donor_pictures"
DONOR_PICS_DIR.mkdir(parents=True, exist_ok=True)
NGO_PICS_DIR = MEDIA_DIR / "ngo_pictures"
NGO_PICS_DIR.mkdir(parents=True, exist_ok=True)
NGO_CERTS_DIR = MEDIA_DIR / "ngo_certificates"
NGO_CERTS_DIR.mkdir(parents=True, exist_ok=True)
DONATION_ITEMS_DIR = MEDIA_DIR / "donation_items"
DONATION_ITEMS_DIR.mkdir(parents=True, exist_ok=True)


def get_secret(key: str, default: str = "") -> str:
    """Safely retrieves a configuration key from st.secrets or os.environ."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)


# Database Configuration
DB_ENGINE = get_secret("DB_ENGINE", "sqlite3").lower()
DB_NAME = get_secret("DB_NAME", str(BACKEND_DIR / "db.sqlite3"))
DB_USER = get_secret("DB_USER", "postgres")
DB_PASSWORD = get_secret("DB_PASSWORD", "")
DB_HOST = get_secret("DB_HOST", "localhost")
DB_PORT = get_secret("DB_PORT", "5432")
DB_SSLMODE = get_secret("DB_SSLMODE", "require" if DB_HOST and DB_HOST != "localhost" else "disable")
DATABASE_URL = get_secret("DATABASE_URL", "")

# AI / Gemini API Configuration
GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")

# Admin Credentials
ADMIN_EMAIL = get_secret("ADMIN_EMAIL", "admin@donation.org")
ADMIN_PASSWORD = get_secret("ADMIN_PASSWORD", "admin123")

# App Secret Key
SECRET_KEY = get_secret("SECRET_KEY", "donation-management-secure-secret-key-2026")
