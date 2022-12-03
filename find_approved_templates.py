#!/usr/bin/env python3

import argparse
from itertools import islice
import logging
import sys
from typing import List

from pywikibot import Site, Page, Category
from nomination import Nomination

logger = logging.getLogger('find_approved_templates')


def main():
    logging.basicConfig(stream=sys.stderr)

    parser = argparse.ArgumentParser()
    parser.add_argument('--max',
                        type=int,
                        help='Maximum number of templates to process (0 means no limit)')
    parser.add_argument('--log-level',
                        choices=['debug', 'info', 'warning', 'error'],
                        default='info',
                        help='Set logging level')
    args = parser.parse_args()

    logger.setLevel(args.log_level.upper())

    process_all(args.max)


def process_all(max: int):
    site = Site('en', 'wikipedia')
    cat = Category(site, 'Pending DYK nominations')
    for page in cat.articles(namespaces="Template", total=max):
        nomination = Nomination(page)
        if nomination.is_approved():
            print(nomination)
            articles = nomination.articles()
            if len(articles) != 1:
                logger.warning("%d articles in %s", len(articles), nomination)
            for a in articles:
                print(f"...{a.title()}")


if __name__ == '__main__':
    main()
