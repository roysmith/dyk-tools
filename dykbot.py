#!/usr/bin/env python3

import argparse
from itertools import islice
import logging
import sys
from typing import List

from pywikibot import Site, Page, Category
from dyk_tools import Nomination

logger = logging.getLogger("find_approved_templates")


def main():
    logging.basicConfig(stream=sys.stderr)
    args = process_command_line()
    logger.setLevel(args.log_level.upper())
    site = Site(args.code, "wikipedia")
    process_nominations(site, args.max)



def process_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--code",
        default="test",
        help="Wikipedia site language code",
    )
    parser.add_argument(
        "--max",
        type=int,
        help="Maximum number of templates to process (default is no limit)",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set logging level",
    )
    return parser.parse_args()


def process_nominations(site: Site, max: int):
    cat = Category(site, "Pending DYK nominations")
    for page in cat.articles(namespaces="Template", total=max):
        nomination = Nomination(page)
        if nomination.is_approved():
            print(nomination)
            articles = nomination.articles()
            for a in articles:
                print(f"...{a.title()}")


if __name__ == "__main__":
    main()
