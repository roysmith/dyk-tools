#!/usr/bin/env python3

import argparse
from collections import namedtuple
from configparser import ConfigParser
from datetime import datetime, timedelta
from itertools import chain
import logging
import os
from pathlib import Path
from typing import Iterable

from pywikibot import Site, Page, Category, User
from pywikibot.exceptions import NoPageError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from dyk_tools import Nomination, HookSet
from dyk_tools import version
from dyk_tools.db.models import BaseModel, BotLog


class IdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return "[%s] %s" % (self.extra["id"], msg), kwargs


Task = namedtuple("Task", ["method", "rights"])


class App:
    def __init__(self):
        self.tasks = {
            "create-db": Task(self.create_db_task, []),
            "add-tags": Task(self.add_tags_task, []),
            "protect": Task(self.protect_task, ["protect"]),
            "unprotect": Task(self.unprotect_task, ["protect"]),
        }
        self.args = self.process_command_line()
        self.basedir = self.get_basedir()

    def configure_logging(self):
        logging_config_args = {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        }
        if self.args.log_file:
            logging_config_args["filename"] = self.args.log_file
        logging.basicConfig(**logging_config_args)

        # Generate a timestamp identifying this run
        id = int(datetime.utcnow().timestamp())

        self.logger = IdAdapter(logging.getLogger("dykbot"), {"id": id})
        self.logger.setLevel(self.args.log_level.upper())

    def run(self):
        self.configure_logging()
        self.site = Site(self.args.mylang)
        self.site.login()
        self.user = User(self.site, self.site.user())
        self.engine = self.get_db_engine()

        self.logger.info("Running on %s", os.uname().nodename)
        self.logger.info("PYWIKIBOT_DIR: %s", os.environ.get("PYWIKIBOT_DIR"))
        self.logger.info("user: %s (%s)", self.user, self.user.groups())
        self.logger.info("basedir: %s", self.basedir)
        self.logger.info("version: %s", version)
        self.logger.info("site: %s", self.site)
        self.logger.info("dry-run: %s", self.args.dry_run)
        self.logger.info("task: %s", self.args.task)

        if self.args.task is None:
            self.logger.warning("No task specified, exiting")
            return

        task = self.tasks[self.args.task]
        if not self.args.dry_run:
            for right in task.rights:
                if right not in self.user.rights():
                    self.logger.error("%s rights: %s", self.user, self.user.rights())
                    self.logger.error("missing '%s', exiting", right)
                    return

        t0 = datetime.utcnow()
        task.method()
        t1 = datetime.utcnow()
        self.logger.info("Task (%s) completed in %s", self.args.task, t1 - t0)

    def create_db_task(self) -> None:
        self.logger.info("Creating %s", list(BaseModel.metadata.tables.keys()))
        BaseModel.metadata.create_all(self.engine)

    def get_basedir(self):
        """Return the application's base directory as a Path.  This is where
        configuration files should be found, log files created, etc.

        """
        if "basedir" in self.args:
            return Path(self.args.basedir)
        else:
            env = os.environ
            return Path(env.get("DYK_TOOLS_BASEDIR") or env.get("HOME"))

    def process_command_line(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--dry-run",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="don't write anything to the wiki, just log what would happen",
        )
        parser.add_argument(
            "--log-level",
            choices=["debug", "info", "warning", "error"],
            default="info",
            help="Set logging level",
        )
        parser.add_argument(
            "--log-file",
            help="log to file (default is to stderr)",
        )
        parser.add_argument(
            "--max",
            type=int,
            help="Maximum number of operations to perform (useful for testing)",
        )
        parser.add_argument(
            "--mylang",
            help="Override mylang config setting",
        )
        parser.add_argument(
            "--basedir",
            default=argparse.SUPPRESS,
            help="Directory for config files (overrides $DYK_TOOLS_BASEDIR)",
        )
        parser.add_argument(
            "--nom",
            default=None,
            help="Process a single nomination (for use with add-tags)",
        )
        parser.add_argument(
            "task",
            nargs="?",
            choices=list(self.tasks),
            help="Task to perform",
        )

        return parser.parse_args()

    def get_db_engine(self):
        configparser = ConfigParser()
        configparser.read(self.basedir / "replica.my.cnf")
        configparser.read(self.basedir / "dykbot.ini")

        data = dict(configparser["client"])
        data["dbname"] = f"{data['user']}__dyk_tools_bot_{self.site.code}"
        if 'url' in data:
            template = "{url}"
        else:
            template = "{scheme}://{user}:{password}@{host}/{dbname}"
        url = template.format(**data)
        data["password"] = "******"
        self.logger.info("Database: %s", template.format(**data))
        return create_engine(url)

    def add_tags_task(self):
        force = False
        if self.args.nom:
            noms = [Page(self.site, self.args.nom)]
            force = True
        else:
            cat = Category(self.site, "Pending DYK nominations")
            noms = cat.articles(namespaces="Template")
        count = 0
        for page in noms:
            nom = Nomination(page)
            try:
                if self.process_one_nomination(nom, force):
                    count += 1
            except NoPageError as ex:
                self.logger.error(
                    "NoPageError while processing [[%s]] (article=[[%s]]), skipping",
                    nom.title(),
                    ex.page.title(),
                )
                raise
                continue
            if self.args.max and count >= self.args.max:
                break
        self.logger.info("Processed %d nomination(s)", count)

    MANAGED_TAGS = frozenset(["Pending DYK biographies", "Pending DYK American hooks"])

    def process_one_nomination(self, nom: Nomination, force: bool = False) -> bool:
        """Process one nomination.  Return True if it wasn't skipped."""
        if (not force) and self.nomination_is_previously_processed(nom):
            self.logger.debug("skipping [[%s]]", nom.title())
            return False
        flags = []
        tags = []
        if nom.is_approved():
            flags.append("Approved")
        if nom.is_biography():
            flags.append("Biography")
            tags.append("Pending DYK biographies")
        if nom.is_american():
            flags.append("American")
            tags.append("Pending DYK American hooks")
        self.logger.info("processing [[%s]] (flags=%s)", nom.title(), flags)
        if not self.args.dry_run:
            nom.mark_processed(tags, self.MANAGED_TAGS)
            self.insert_log_entry(nom)
        return True

    def nomination_is_previously_processed(self, nom) -> bool:
        with Session(self.engine) as session:
            stmt = select(BotLog).where(BotLog.title == nom.title())
            data = session.scalars(stmt).first()
            return bool(data)

    def insert_log_entry(self, nom) -> None:
        with Session(self.engine) as session:
            entry = BotLog(title=nom.title(), timestamp_utc=datetime.utcnow())
            session.add(entry)
            session.commit()

    def protect_task(self) -> None:
        count = 0
        for target in self.protectable_targets():
            if self.protect_target(target):
                count += 1
            if self.args.max and count >= self.args.max:
                break
        self.logger.info("Protected %d page(s)", count)

    def protect_target(self, target: Page) -> bool:
        """Try to protect a target.  Returns True if it does,
        False on any kind of failure.

        """
        if not target.exists():
            self.logger.warning("%s does not exist, skipping", target)
            return False

        if target.isRedirectPage():
            self.logger.warning("%s is a redirect, skipping", target)
            return False

        if self.args.dry_run:
            self.logger.info("found %s", target)
        else:
            self.logger.info("protecting %s", target)
            self.logger.debug("applicable: %s", target.applicable_protections())
            username = self.site.username()
            target.protect(
                f"[[User:{username}/Protect Task]]",
                {"move": "sysop"},
            )
        return True

    def protectable_targets(self) -> Iterable[Page]:
        hook_set_titles = chain(
            ["Template:Did you know"],
            [f"Template:Did you know/Queue/{i}" for i in range(1, 8)],
        )
        for t in hook_set_titles:
            hook_set = HookSet(Page(self.site, t))
            for target in hook_set.targets():
                yield target

    def unprotect_task(self) -> None:
        count = 0
        for target in self.unprotectable_targets():
            self.unprotect_target(target)
            count += 1
            if self.args.max and count >= self.args.max:
                break
        self.logger.info("Unprotected %d page(s)", count)

    def unprotect_target(self, target: Page) -> None:
        self.logger.info("unprotecting %s", target)
        username = self.site.username()
        target.protect(
            f"[[User:{username}/Unprotect Task]]",
            {"move": ""},
        )

    def unprotectable_targets(self) -> Iterable[Page]:
        """Examine the bot's protection log for targets that need to be
        unprotected.  A target qualifies if the most recent action for that
        page in the log is 'protect' by the bot user and it is not included
        in any of the active hook sets.

        """
        current_targets = set(self.protectable_targets())
        seen_titles = set()
        end_time = self.site.server_time() - timedelta(days=9)
        for event in self.user.logevents(logtype="protect", end=end_time):
            if event["title"] in seen_titles:
                continue
            seen_titles.add(event["title"])
            if event["action"] != "protect":
                continue
            page = Page(self.site, event["title"])
            if not page.exists():
                self.logger.warning("%s doesn't exist", page)
                continue
            if page in current_targets:
                self.logger.debug("%s still needs protection, skipping", page)
                continue
            page_events = self.site.logevents(logtype="protect", page=page, total=1)
            last_event = next(page_events, None)
            if last_event["user"] != self.user.username:
                continue
            yield page


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
