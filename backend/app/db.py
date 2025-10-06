from __future__ import annotations
import os
import sys
import logging

log = logging.getLogger("app.db")

# Railway (или локально) — если переменная пуста, работаем в демо-режиме без БД
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

engine = None
SessionLocal = None


class _DummySession:
    """Ничего не делает, но совместим с ожиданиями вызова .close()/.commit()."""
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def close(self): pass
    def commit(self): pass
    def rollback(self): pass


class _DummySessionFactory:
    def __call__(self, *args, **kwargs):  # SessionLocal()-совместимый
        return _DummySession()


def _setup():
    """Создаёт движок и фабрику сессий, либо переключает на no-op сессии."""
    global engine, SessionLocal

    if not DATABASE_URL:
        log.warning("[db] DATABASE_URL not set; skipping DB bootstrap (demo mode)")
        engine = None
        SessionLocal = _DummySessionFactory()
        return

    # SQLAlchemy может быть не установлен на ранних этапах
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
    except ModuleNotFoundError as e:
        log.error(f"[db] SQLAlchemy not available: {e}; skipping DB bootstrap")
        engine = None
        SessionLocal = _DummySessionFactory()
        return

    # create_engine может упасть из-за отсутствия драйвера (psycopg2/psycopg)
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        log.info("[db] DB engine created")
    except ModuleNotFoundError as e:
        log.error(f"[db] DB driver missing: {e}; skipping DB bootstrap (demo mode)")
        engine = None
        SessionLocal = _DummySessionFactory()


def get_db():
    """
    Провайдер сессии для Depends.
    В демо-режиме возвращает no-op сессию, чтобы код не падал.
    """
    db = SessionLocal() if SessionLocal else _DummySession()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass


# Инициализация при импорте модуля
_setup()


if __name__ == "__main__":
    # Позволяет безопасно вызывать `python app/db.py` из start.sh
    if engine is None:
        print("[db] No engine (demo mode). Nothing to bootstrap.")
        sys.exit(0)

    # Здесь можно выполнить инициализацию схемы:
    # from .models_sql import Base
    # Base.metadata.create_all(engine)
    print("[db] Engine available. (Add metadata.create_all(engine) here if needed.)")
    sys.exit(0)
