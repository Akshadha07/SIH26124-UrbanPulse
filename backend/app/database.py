from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# SQLite compatibility check for thread access
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all database tables on startup and apply light migrations if needed."""
    import app.models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)

    # SQLite schema migration safeguard for added columns
    if settings.DATABASE_URL.startswith("sqlite"):
        import sqlite3
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cols = [row[1] for row in cur.execute("PRAGMA table_info(hazards)").fetchall()]
            new_cols = [
                ("distinct_bus_count", "INTEGER DEFAULT 1"),
                ("priority_explanation", "TEXT"),
                ("verification_passes", "INTEGER DEFAULT 0"),
                ("resolved_at", "TIMESTAMP"),
            ]
            for col_name, col_type in new_cols:
                if col_name not in cols:
                    cur.execute(f"ALTER TABLE hazards ADD COLUMN {col_name} {col_type}")
            conn.commit()
            conn.close()
        except Exception:
            pass
