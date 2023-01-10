#!/usr/bin/env python3

import argparse
from datetime import datetime
from itertools import islice
import logging
import os
import time

from pywikibot import Site, Category
from pywikibot.exceptions import NoPageError
from dyk_tools import Nomination
from dyk_tools.version import version_string

class IdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return '[%s] %s' % (self.extra['id'], msg), kwargs
        

class App:
    def run(self):
        t0 = datetime.utcnow()
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
        self.logger = IdAdapter(logging.getLogger("dykbot"), {'id': id})

        self.logger.setLevel(self.args.log_level.upper())
        self.nomination_count = 0
        self.site = Site(self.args.mylang)
        self.logger.info("Running on %s", os.uname().nodename)
        self.logger.info("version: %s", version_string)
        self.logger.info("site: %s", self.site)
        self.logger.info("dry-run: %s", self.args.dry_run)

        self.process_nominations()

        t1 = datetime.utcnow()
        self.logger.info(
            "Processed %d nomination(s) in %s", self.nomination_count, t1 - t0
        )

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
        parser.add_argument("--log-file", help="log to file (default is to stderr)")
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

    def process_nominations(self):
        cat = Category(self.site, "Pending DYK nominations")
        for page in cat.articles(namespaces="Template"):
            try:
                self.process_one_nomination(page)
            except NoPageError as ex:
                self.logger.error(
                    "NoPageError while processing [[%s]] (article=[[%s]]), skipping",
                    page.title(),
                    ex.page.title(),
                )
                continue
            if self.args.max and self.nomination_count >= self.args.max:
                self.logger.info(
                    "Stopping early after %d nominations", self.nomination_count
                )
                return

    MANAGED_TAGS = frozenset(
        ["Pending DYK biographies", "Pending DYK American hooks"]
    )

    def process_one_nomination(self, page):
        nom = Nomination(page)
        if nom.is_previously_processed():
            self.logger.debug("skipping [[%s]]", nom.page.title())
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
        self.logger.info("processing [[%s]] (flags=%s)", nom.page.title(), flags)
        self.nomination_count += 1
        if not self.args.dry_run:
            nom.mark_processed(tags, self.MANAGED_TAGS)


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
