#!/usr/bin/env python3

from datetime import datetime
from pprint import pprint
from typing import Optional

from sqlalchemy import String, Index
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
    title: Mapped[str] = mapped_column(String(255))
    timestamp_utc: Mapped[datetime]

    # 190 prefix length avoids 767 byte index limit.
    __table_args__ = (Index("ix_title", "title", mysql_length=190),)
