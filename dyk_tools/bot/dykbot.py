#!/usr/bin/env python3

import argparse
from configparser import ConfigParser
from datetime import datetime
from itertools import islice
import logging
import os
from pathlib import Path
import time

from pywikibot import Site, Category
from pywikibot.exceptions import NoPageError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from dyk_tools import Nomination
from dyk_tools.version import version_string
from dyk_tools.db.models import BotLog


class IdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return "[%s] %s" % (self.extra["id"], msg), kwargs


class App:
    def run(self):
        t0 = datetime.utcnow()
        self.basedir = self.get_basedir()
        self.args = self.process_command_line()
        logging_config_args = {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        }
        if self.args.log_file:
            logging_config_args["filename"] = self.args.log_file
        logging.basicConfig(**logging_config_args)

        # Generate a timestamp identifying this run
        id = int(t0.timestamp())
        self.logger = IdAdapter(logging.getLogger("dykbot"), {"id": id})

        self.logger.setLevel(self.args.log_level.upper())
        self.nomination_count = 0
        self.site = Site(self.args.mylang)

        self.logger.info("Running on %s", os.uname().nodename)
        self.logger.info("Basedir: %s", self.basedir)
        self.logger.info("version: %s", version_string)
        self.logger.info("site: %s", self.site)
        self.logger.info("dry-run: %s", self.args.dry_run)

        self.engine = self.get_db_engine()

        self.process_nominations()

        t1 = datetime.utcnow()
        self.logger.info(
            "Processed %d nomination(s) in %s", self.nomination_count, t1 - t0
        )

    def get_basedir(self):
        """Return the application's base directory as a Path.  This is where
        configuration files should be found, log files created, etc.

        """
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
            help="Maximum number of nominations to touch",
        )
        parser.add_argument(
            "--mylang",
            help="Override mylang config setting",
        )
        return parser.parse_args()

    def get_db_engine(self):
        configparser = ConfigParser()
        configparser.read(self.basedir / "replica.my.cnf")
        configparser.read(self.basedir / "dykbot.ini")

        data = dict(configparser["client"])
        data["dbname"] = f"{data['user']}__dyk_tools_bot_{self.site.code}"
        template = "{scheme}://{user}:{password}@{host}/{dbname}"
        url = template.format(**data)
        data["password"] = "******"
        self.logger.info("Database: %s", template.format(**data))
        return create_engine(url)

    def process_nominations(self):
        cat = Category(self.site, "Pending DYK nominations")
        for page in cat.articles(namespaces="Template"):
            nom = Nomination(page)
            try:
                self.process_one_nomination(nom)
            except NoPageError as ex:
                self.logger.error(
                    "NoPageError while processing [[%s]] (article=[[%s]]), skipping",
                    nom.title(),
                    ex.page.title(),
                )
                continue
            if self.args.max and self.nomination_count >= self.args.max:
                self.logger.info(
                    "Stopping early after %d nominations", self.nomination_count
                )
                return

    MANAGED_TAGS = frozenset(["Pending DYK biographies", "Pending DYK American hooks"])

    def process_one_nomination(self, nom):
        if self.nomination_is_previously_processed(nom):
            self.logger.debug("skipping [[%s]]", nom.title())
            return
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
        self.nomination_count += 1
        if not self.args.dry_run:
            nom.mark_processed(tags, self.MANAGED_TAGS)
            self.insert_log_entry(nom)

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


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
