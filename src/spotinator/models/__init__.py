from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

from models.log_entry import LogEntry

engine = create_engine("sqlite:///./test.db")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
