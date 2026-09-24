"""
Database initialization and ORM connection layer for Streamlit.
Supports SQLite and PostgreSQL via Streamlit secrets or environment variables.
"""

import os
import sys
from pathlib import Path
import streamlit as st

from src.config import (
    BASE_DIR,
    BACKEND_DIR,
    DB_ENGINE,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_SSLMODE,
    DATABASE_URL,
    SECRET_KEY,
    MEDIA_DIR,
)

# Ensure Backend folder is in sys.path so models and apps are importable
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


@st.cache_resource
def init_database():
    """
    Initializes Django ORM with the configured database.
    Uses st.cache_resource so it executes only once per application run.
    """
    import django
    from django.conf import settings

    if not settings.configured:
        # Determine database config
        if DATABASE_URL:
            import urllib.parse
            url = urllib.parse.urlparse(DATABASE_URL)
            db_config = {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": url.path[1:] if url.path else DB_NAME,
                "USER": url.username or DB_USER,
                "PASSWORD": url.password or DB_PASSWORD,
                "HOST": url.hostname or DB_HOST,
                "PORT": str(url.port or DB_PORT),
                "OPTIONS": {
                    "sslmode": DB_SSLMODE,
                },
            }
        elif DB_ENGINE == "postgresql":
            db_config = {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": DB_NAME,
                "USER": DB_USER,
                "PASSWORD": DB_PASSWORD,
                "HOST": DB_HOST,
                "PORT": DB_PORT,
                "OPTIONS": {
                    "sslmode": DB_SSLMODE,
                },
            }
        else:
            # Default SQLite
            sqlite_path = Path(DB_NAME)
            if not sqlite_path.is_absolute():
                sqlite_path = BACKEND_DIR / "db.sqlite3"
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            db_config = {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(sqlite_path),
            }

        settings.configure(
            BASE_DIR=str(BACKEND_DIR),
            SECRET_KEY=SECRET_KEY,
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "donor",
                "notifications.apps.NotificationsConfig",
                "users",
            ],
            DATABASES={"default": db_config},
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            MEDIA_URL="/media/",
            MEDIA_ROOT=str(MEDIA_DIR),
            TIME_ZONE="UTC",
            USE_TZ=True,
        )

        django.setup()

        # Run migrations if necessary
        try:
            from django.core.management import call_command
            call_command("migrate", interactive=False, verbosity=0)
        except Exception as e:
            print(f"Migration notice: {e}")

    return True


# Initialize on import
init_database()
