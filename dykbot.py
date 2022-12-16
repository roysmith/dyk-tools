#!/usr/bin/env python3

import argparse
from datetime import datetime
from itertools import islice
import logging
from pathlib import Path

from pywikibot import Site, Category
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
        self.site = Site()
        self.logger.info("Starting run, site=%s, dry-run=%s", self.site, self.args.dry_run)
        self.process_nominations()
        t1 = datetime.utcnow()
        self.logger.info("Done.  Processed %d nominations", self.nomination_count)


    def process_command_line(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--dry-run",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="if dry-run, don't write anything to the wiki, just log what would happen (default=dry-run)",
        )
        parser.add_argument(
            "--log-level",
            choices=["debug", "info", "warning", "error"],
            default="info",
            help="Set logging level",
        )
        return parser.parse_args()


    def process_nominations(self):
        cat = Category(self.site, "Pending DYK nominations")
        for page in cat.articles(namespaces="Template"):
            nom = Nomination(page)
            self.nomination_count += 1
            flags = []
            if nom.is_approved():
                flags.append("Approved")
            if nom.is_biography():
                flags.append("Biography")
            if nom.is_american():
                flags.append("American")
            self.logger.debug("[[%s]] %s", nom.page.title(), flags)


if __name__ == "__main__":
    app = App()
    app.main()