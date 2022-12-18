#!/usr/bin/env python3

import argparse
from datetime import datetime
from itertools import islice
import logging
from pathlib import Path

from pywikibot import Site, Category
from pywikibot.exceptions import NoPageError
from dyk_tools import Nomination


class App:
    def main(self):
        logging.basicConfig(
            filename=Path.home() / "dykbot.log",
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        self.args = self.process_command_line()
        self.logger = logging.getLogger("dykbot")
        self.logger.setLevel(self.args.log_level.upper())
        t0 = datetime.utcnow()
        self.nomination_count = 0
        self.site = Site(self.args.mylang)
        self.logger.info(
            "Starting run, site=%s, dry-run=%s", self.site, self.args.dry_run
        )
        self.process_nominations()
        t1 = datetime.utcnow()
        self.logger.info(
            "Done.  Processed %d nominations in %s", self.nomination_count, t1 - t0
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

    def process_one_nomination(self, page):
        nom = Nomination(page)
        if nom.is_previously_processed():
            self.logger.debug("[[%s]]: Been there, done that", nom.page.title())
            return
        flags = []
        cats = []
        if nom.is_approved():
            flags.append("Approved")
        if nom.is_biography():
            flags.append("Biography")
            cats.append("Category:Pending DYK biographies")
        if nom.is_american():
            flags.append("American")
            cats.append("Category:Pending DYK American hooks")
        self.logger.debug("[[%s]] %s", nom.page.title(), flags)
        self.nomination_count += 1
        if not self.args.dry_run:
            nom.mark_processed(cats, ["Category:Pending DYK biographies", "Category:Pending DYK American hooks"])


if __name__ == "__main__":
    app = App()
    app.main()
