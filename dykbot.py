#!/usr/bin/env python3

import argparse
from itertools import islice
import logging
from pathlib import Path

from pywikibot import Site, Category
from dyk_tools import Nomination

logger = logging.getLogger("dykbot")


def main():
    logging.basicConfig(
        filename=Path.home() / "dykbot.log",
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = process_command_line()
    logger.setLevel(args.log_level.upper())

    site = Site()
    process_nominations(site, args.dry_run)


def process_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_false",
        help="Don't write anything to the wiki, just log what would happen (default=%(default)s)",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set logging level",
    )
    return parser.parse_args()


def process_nominations(site: Site, dry_run: bool):
    logger.info("Starting run, site=%s, dry-run=%s", site, dry_run)
    cat = Category(site, "Pending DYK nominations")
    for page in cat.articles(namespaces="Template"):
        nom = Nomination(page)
        flags = []
        if nom.is_approved():
            flags.append("Approved")
        if nom.is_biography():
            flags.append("Biography")
        if nom.is_american():
            flags.append("American")
        logger.debug("[[%s]] %s", nom.page.title(), flags)


if __name__ == "__main__":
    main()
