# Structured JSON logger with daily rotation (14-day retention)

from pathlib import Path
import logging, json, uuid
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.msg if isinstance(record.msg, dict) else {"message": record.getMessage()}
        return json.dumps(msg, default=str, separators=(",", ":"), ensure_ascii=False)

def setup_logger() -> logging.Logger:
    handler = TimedRotatingFileHandler(
        LOG_DIR / "fastapi_security.log",
        when="midnight",
        interval=1,
        backupCount=14,
        encoding="utf-8",
        

    )
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("fastapi_security")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

def new_request_id() -> str:
    return uuid.uuid4().hex
