import os
import tempfile
import logging
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_sqlite_fallback_url() -> str:
    """Determine a safe, writable SQLite database URL for local dev or serverless runtimes."""
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "sqlite:////tmp/automind_local.db"

    try:
        test_file = "./.db_write_test"
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        return "sqlite:///./automind_local.db"
    except (OSError, IOError):
        tmp_dir = tempfile.gettempdir()
        return f"sqlite:///{os.path.join(tmp_dir, 'automind_local.db')}"

def create_db_engine(db_url: str):
    engine_kwargs = {"pool_pre_ping": True}
    if db_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
    else:
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_recycle"] = 300
        engine_kwargs["connect_args"] = {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
            "charset": "utf8mb4",
        }

    eng = create_engine(db_url, **engine_kwargs)
    
    # Resilient connection check with retries for container startup
    if not db_url.startswith("sqlite"):
        connected = False
        max_attempts = 3 if os.environ.get("VERCEL") else 5
        for attempt in range(1, max_attempts + 1):
            try:
                with eng.connect() as conn:
                    conn.execute(text("SELECT 1"))
                connected = True
                logger.info(f"Successfully connected to database at {db_url}")
                break
            except Exception as e:
                logger.warning(f"Database connection attempt {attempt}/{max_attempts} failed: {e}")
                if attempt < max_attempts:
                    time.sleep(1 if os.environ.get("VERCEL") else 2)

        if not connected:
            fallback_url = get_sqlite_fallback_url()
            logger.warning(f"Unable to connect to MySQL database at {db_url} after {max_attempts} attempts.")
            logger.warning(f"Falling back to SQLite database ({fallback_url}) for execution.")
            eng = create_engine(fallback_url, connect_args={"check_same_thread": False, "timeout": 30}, pool_pre_ping=True)
    
    return eng

engine = create_db_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependency for providing database sessions with automated rollback on error."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


