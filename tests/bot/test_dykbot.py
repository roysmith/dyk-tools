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
        app.logger = logging.getLogger("dykbot")
        return app

    @pytest.mark.parametrize(
        "logevents, protectables, expected",
        [
            (
                [],
                [],
                [],
            ),
            (
                [
                    {"title": "foo", "action": "protect"},
                ],
                [],
                ["foo"],
            ),
            (
                [
                    {"title": "foo", "action": "protect"},
                    {"title": "bar", "action": "protect"},
                ],
                [],
                ["foo", "bar"],
            ),
            (
                [
                    {"title": "t1", "action": "protect"},
                    {"title": "t2", "action": "protect"},
                    {"title": "t3", "action": "protect"},
                ],
                ["t1"],
                ["t2", "t3"],
            ),
            (
                [
                    {"title": "t1", "action": "unprotect"},
                    {"title": "t2", "action": "protect"},
                    {"title": "t3", "action": "protect"},
                ],
                [],
                ["t2", "t3"],
            ),
            (
                [
                    {"title": "t1", "action": "unprotect"},
                    {"title": "t2", "action": "protect"},
                    {"title": "t3", "action": "protect"},
                ],
                ["t2"],
                ["t3"],
            ),
        ],
    )
    def test_return_value(self, app, site, Page, logevents, protectables, expected):
        app.user.logevents.return_value = logevents
        app.protectable_targets.return_value = [
            Page(site, title) for title in protectables
        ]

        targets = app.unprotectable_targets()

        titles = {page.title for page in targets}
        assert titles == set(expected)
