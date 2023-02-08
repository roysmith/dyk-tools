from datetime import datetime
import logging
from pathlib import Path
import pytest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


from dyk_tools.bot.dykbot import App
from dyk_tools.db.models import BaseModel, BotLog


@pytest.fixture
def engine():
    return create_engine("sqlite://", echo=True)


@pytest.fixture(autouse=True)
def create_db(engine):
    BaseModel.metadata.create_all(engine)
    yield
    BaseModel.metadata.drop_all(engine)


def test_construct(mocker):
    mocker.patch("sys.argv", ["program.py"])
    app = App()
    assert app


def test_cli_basedir(mocker):
    mocker.patch("sys.argv", ["program.py", "--basedir=/foo/bar"])
    app = App()
    assert app.basedir == Path("/foo/bar")


class TestProcessOneNomination:
    @pytest.fixture
    def app(self, mocker, engine):
        mocker.patch("sys.argv", ["program.py"])
        app = App()
        app.logger = logging.getLogger("dykbot")
        app.args = mocker.Mock()
        app.args.dry_run = False
        app.engine = engine
        return app

    @pytest.fixture(autouse=True)
    def set_debug(self, caplog):
        caplog.set_level("DEBUG")

    @pytest.fixture
    def nom_foo(self, mocker):
        nom = mocker.Mock()
        nom.title.return_value = "Foo"
        return nom

    def test_new_nom_is_processed(self, engine, caplog, nom_foo, app):
        app.process_one_nomination(nom_foo)

        assert "processing [[Foo]]" in caplog.text
        with Session(engine) as session:
            stmt = select(BotLog).where(BotLog.title == "Foo")
            assert len(session.scalars(stmt).all()) == 1

    def test_processed_nom_is_skipped(self, engine, caplog, nom_foo, app):
        with Session(engine) as session:
            entry = BotLog(title="Foo", timestamp_utc=datetime.utcnow())
            session.add(entry)
            session.commit()

        app.process_one_nomination(nom_foo)

        assert "skipping [[Foo]]" in caplog.text
        with Session(engine) as session:
            stmt = select(BotLog).where(BotLog.title == "Foo")
            assert len(session.scalars(stmt).all()) == 1
