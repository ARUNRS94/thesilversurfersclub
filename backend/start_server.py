"""Windows/offline entry point for the SeniorConnect FastAPI server.

This module is intentionally small so it can be packaged with PyInstaller:
    pyinstaller --onefile backend/start_server.py
"""
from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles


def app_root() -> Path:
    """Return the application root for source or PyInstaller execution."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def configure_environment(root: Path) -> None:
    data_dir = root / "data"
    uploads_dir = root / "uploads"
    data_dir.mkdir(exist_ok=True)
    uploads_dir.mkdir(exist_ok=True)
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{data_dir / 'seniorconnect.db'}")
    os.environ.setdefault("UPLOAD_DIR", str(uploads_dir))


def create_app():
    root = app_root()
    configure_environment(root)

    # Import after DATABASE_URL/UPLOAD_DIR are set so SQLAlchemy uses the local
    # offline/on-premise database beside the executable.
    from app.main import app
    from app.seed import db as seed_db

    seed_db.close()

    frontend_dist = root / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    if os.environ.get("SENIORCONNECT_OPEN_BROWSER", "1") == "1":
        webbrowser.open(f"http://127.0.0.1:{port}")
    uvicorn.run(create_app(), host="127.0.0.1", port=port)
