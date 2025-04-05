import logging
import logging.handlers
from models import LogEntry, engine
from sqlmodel import Session
import config


class DBHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        db = Session(engine)
        try:
            entry = LogEntry(message=log_entry)
            db.add(entry)
            db.commit()
        except Exception as e:
            print(f"Error writing log entry to database: {e} -> {log_entry}")
            db.rollback()
        finally:
            db.close()


BASE_LOG = logging.getLogger(config.LOGGER_NAME)
BASE_LOG.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)

db_handler = DBHandler()
db_formatter = logging.Formatter(
    "%(process)d:%(asctime)s:%(levelname)s:%(name)s:%(message)s"
)
db_handler.setFormatter(db_formatter)
db_handler.setLevel(logging.DEBUG)

BASE_LOG.addHandler(console_handler)
BASE_LOG.addHandler(db_handler)
BASE_LOG.propagate = False

logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("traitlets").setLevel(logging.WARNING)

BASE_LOG.info("Base log initialized.")
