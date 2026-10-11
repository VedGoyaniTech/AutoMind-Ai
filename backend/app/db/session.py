import logging
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)

def create_db_engine(db_url: str):
    engine_kwargs = {"pool_pre_ping": True}
    if db_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
    else:
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_recycle"] = 3600
        engine_kwargs["connect_args"] = {"connect_timeout": 5}

    eng = create_engine(db_url, **engine_kwargs)
    
    # Resilient connection check with retries for container startup
    if not db_url.startswith("sqlite"):
        connected = False
        max_attempts = 5
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
                    time.sleep(2)

        if not connected:
            logger.warning(f"Unable to connect to MySQL database at {db_url} after {max_attempts} attempts.")
            logger.warning("Falling back to local SQLite database (sqlite:///./automind_local.db) for local development.")
            fallback_url = "sqlite:///./automind_local.db"
            eng = create_engine(fallback_url, connect_args={"check_same_thread": False, "timeout": 30}, pool_pre_ping=True)
    
    return eng

engine = create_db_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependency for providing database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

