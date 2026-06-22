"""Windows/offline entry point for the SeniorConnect FastAPI server.

This module is intentionally small so it can be packaged with PyInstaller:
    pyinstaller --onefile backend/start_server.py
"""
from __future__ import annotations

import os
import sys
import traceback
import webbrowser
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles

# PyInstaller does not always detect passlib bcrypt handlers because passlib
# loads them dynamically from its registry at runtime. Keep this import so the
# one-file Windows executable includes the handler required by app.core.security.
import passlib.handlers.bcrypt  # noqa: F401


def app_root() -> Path:
    """Return the application root for source or PyInstaller execution."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def write_startup_error(root: Path, exc: BaseException) -> Path:
    """Persist startup errors so double-click users can send diagnostics."""
    log_path = root / "seniorconnect-error.log"
    log_path.write_text("SeniorConnect failed to start:\n\n" + "".join(traceback.format_exception(exc)), encoding="utf-8")
    return log_path


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
    else:
        print(f"Warning: frontend bundle not found at {frontend_dist}")
    return app


def main() -> None:
    root = app_root()
    try:
        port = int(os.environ.get("PORT", "8000"))
        app = create_app()
        url = f"http://127.0.0.1:{port}"
        print(f"SeniorConnect is running at {url}")
        print("Keep this window open while using the software.")
        if os.environ.get("SENIORCONNECT_OPEN_BROWSER", "1") == "1":
            webbrowser.open(url)
        uvicorn.run(app, host="127.0.0.1", port=port)
    except Exception as exc:  # noqa: BLE001 - top-level executable diagnostics
        log_path = write_startup_error(root, exc)
        print(f"SeniorConnect failed to start. Details were saved to: {log_path}")
        traceback.print_exception(exc)
        raise


if __name__ == "__main__":
    main()
