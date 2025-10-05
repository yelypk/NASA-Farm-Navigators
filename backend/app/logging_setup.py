# backend/app/logging_setup.py
import logging
import os
import sys

def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # подробные логи SQLAlchemy при DEBUG
    if level == "DEBUG":
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)   # SQL запросы
        logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)     # пул соединений
