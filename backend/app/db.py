# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging, os

log = logging.getLogger("app.db")

DATABASE_URL = os.getenv("DATABASE_URL")  # уже настроено в Railway
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
