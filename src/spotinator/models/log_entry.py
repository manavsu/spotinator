from typing import Optional
from sqlmodel import Field, SQLModel
import time


class LogEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: int = Field(default_factory=lambda: int(time.time()), index=True)
    message: str

    def __repr__(self):
        return f"<Log Entry id:{self.id} timestamp:{self.timestamp} message:{self.message}>"
