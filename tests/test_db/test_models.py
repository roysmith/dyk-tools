from datetime import datetime
import pytest
from dyk_tools.db.models import BaseModel, BotLog

from sqlalchemy import create_engine, Table
from sqlalchemy.orm import Session


@pytest.fixture
def engine():
    return create_engine("sqlite://", echo=True)


@pytest.fixture
def db(engine):
    BaseModel.metadata.create_all(engine)
    yield
    BaseModel.metadata.drop_all(engine)


def test_table_creation(db):
    bot_log = Table("bot_log", BaseModel.metadata, autoload_with=engine)
    columns = {col.name for col in bot_log.columns}
    assert columns == {"id", "title", "timestamp_utc"}


def test_log_entry_insertion(engine, db):
    with Session(engine) as session:
        entry = BotLog(title="Foo", timestamp_utc=datetime.utcnow())
        session.add(entry)
        session.commit()
        assert entry.id > 0


def test_log_entry_query_by_id(engine, db):
    with Session(engine) as session1:
        entry1 = BotLog(title="Foo", timestamp_utc=datetime.utcnow())
        session1.add(entry1)
        session1.commit()
        id = entry1.id
    with Session(engine) as session2:
        entry2 = session2.get(BotLog, id)
        assert entry2.id > 0
        assert entry2.id == entry1.id
        assert entry2.title == "Foo"
