#!/usr/bin/env python3

from datetime import datetime
from pprint import pprint
from typing import Optional

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class BaseModel(DeclarativeBase):
    pass


class BotLog(BaseModel):
    __tablename__ = "bot_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)
    timestamp_utc: Mapped[datetime]
