from datetime import datetime
import logging
from pathlib import Path
import pytest

from pywikibot.logentries import LogEntry
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


def test_correct_task_is_run(mocker):
    mocker.patch("sys.argv", ["program.py", "create-db"])
    create_db_task = mocker.patch(
        "dyk_tools.bot.dykbot.App.create_db_task", autospec=True
    )
    mocker.patch("dyk_tools.bot.dykbot.Page", autospec=True)
    mocker.patch("dyk_tools.bot.dykbot.Site", autospec=True)
    mocker.patch("dyk_tools.bot.dykbot.User", autospec=True)
    app = App()
    app.run()
    create_db_task.assert_called_once()


class TestProcessOneNomination:
    @pytest.fixture
    def app(self, mocker, engine):
        mocker.patch("sys.argv", ["program.py"])
        app = App()
        app.logger = logging.getLogger("dykbot")
        app.logger.setLevel(logging.DEBUG)
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


class TestUnprotectableTargets:
    @pytest.fixture(autouse=True)
    def Page(self, mocker):
        def _Page(site, title):
            page = mocker.MagicMock()
            page.title = title
            page.__eq__ = lambda this, other: this.title == other.title
            page.__hash__ = lambda o: hash(o.title)
            return page

        Page = mocker.patch("dyk_tools.bot.dykbot.Page", autospec=True)
        Page.side_effect = _Page
        return Page

    @pytest.fixture
    def app(self, mocker):
        mocker.patch("sys.argv", ["program.py"])
        app = App()
        app.site = mocker.Mock()
        app.user = mocker.Mock()
        app.protectable_targets = mocker.Mock()
        app.site.server_time.return_value = datetime.utcnow()
        app.user.username = "bot"
        app.logger = logging.getLogger("dykbot")
        return app

    @pytest.mark.parametrize(
        "event_data, protectables, expected",
        [
            (
                [],
                [],
                [],
            ),
            (
                [
                    {"logid": 1, "title": "t1", "action": "protect", "user": "bot"},
                ],
                [],
                ["t1"],
            ),
            (
                [
                    {"logid": 11, "title": "t1", "action": "protect", "user": "bot"},
                    {"logid": 12, "title": "t2", "action": "protect", "user": "bot"},
                ],
                [],
                ["t1", "t2"],
            ),
            (
                [
                    {"logid": 21, "title": "t1", "action": "protect", "user": "bot"},
                    {"logid": 22, "title": "t2", "action": "protect", "user": "bot"},
                    {"logid": 23, "title": "t3", "action": "protect", "user": "bot"},
                ],
                ["t1"],
                ["t2", "t3"],
            ),
            (
                [
                    {"logid": 31, "title": "t1", "action": "unprotect", "user": "bot"},
                    {"logid": 32, "title": "t2", "action": "protect", "user": "bot"},
                    {"logid": 33, "title": "t3", "action": "protect", "user": "bot"},
                ],
                [],
                ["t2", "t3"],
            ),
            (
                [
                    {"logid": 41, "title": "t1", "action": "unprotect", "user": "bot"},
                    {"logid": 42, "title": "t2", "action": "protect", "user": "bot"},
                    {"logid": 43, "title": "t3", "action": "protect", "user": "bot"},
                ],
                ["t2"],
                ["t3"],
            ),
            (
                [
                    {"logid": 51, "title": "t1", "action": "unprotect", "user": "bot"},
                    {"logid": 52, "title": "t1", "action": "protect", "user": "bot"},
                    {"logid": 53, "title": "t2", "action": "protect", "user": "bot"},
                ],
                [],
                ["t2"],
            ),
            (
                [
                    {"logid": 61, "title": "t1", "action": "protect", "user": "bot"},
                    {"logid": 62, "title": "t1", "action": "unprotect", "user": "bot"},
                    {"logid": 63, "title": "t2", "action": "protect", "user": "bot"},
                ],
                [],
                ["t1", "t2"],
            ),
            (
                [
                    {"logid": 71, "title": "t1", "action": "protect", "user": "other"},
                    {"logid": 72, "title": "t1", "action": "protect", "user": "bot"},
                ],
                [],
                [],
            ),
        ],
    )
    def test_return_value(self, app, site, Page, event_data, protectables, expected):
        log_entries = [LogEntry(data, site) for data in event_data]
        app.user.logevents.return_value = [e for e in log_entries if e["user"] == "bot"]
        app.site.logevents.side_effect = lambda **kw: (
            e for e in log_entries if e["title"] == kw["page"].title
        )
        app.protectable_targets.return_value = [
            Page(site, title) for title in protectables
        ]

        targets = app.unprotectable_targets()

        titles = {page.title for page in targets}
        assert titles == set(expected)
