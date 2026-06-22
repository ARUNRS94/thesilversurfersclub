from fastapi import FastAPI
from sqlalchemy import inspect, text
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db import Base, engine
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

def ensure_runtime_schema_updates():
    """Apply tiny backward-compatible SQLite/schema updates for existing local DBs.

    Base.metadata.create_all creates new tables but does not add columns to existing
    tables, so local sqlite databases created before a migration can miss new
    nullable columns until Alembic is run. This keeps login working in dev/demo
    environments while the Alembic migration remains the source of truth.
    """
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "allowed_pages" not in user_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE users ADD COLUMN allowed_pages TEXT"))

ensure_runtime_schema_updates()
app = FastAPI(title="SeniorConnect API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")
