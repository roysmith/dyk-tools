#!/usr/bin/env python3

import argparse
from itertools import islice
import logging
import sys
from typing import List

from pywikibot import Site, Page, Category
import mwparserfromhell as mw

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
    for nomination in cat.articles(namespaces="Template", total=max):
        process_nomination(nomination)


def process_nomination(nomination: Page) -> None:
    print(nomination)
    if not is_approved(nomination):
        return
    articles = get_articles(nomination)
    if len(articles) != 1:
        logger.warning("%d articles in %s", len(articles), nomination)


def is_approved(nomination: Page) -> bool:
    """Return True if the nomination has been approved.

    """
    for image in nomination.imagelinks():
        if image.title() == 'File:Symbol confirmed.svg':
            return True
    return False


def get_articles(nomination: Page) -> List[Page]:
    """Return the articles included in the nomination.

    In theory, all nominations should include at least one article,
    but nothing enforces that, so this could possibly return zero
    articles.

    """
    pages = []
    for t, params in nomination.templatesWithParams():
        if t.title == 'DYK nompage links':
            print(t)
            pages.append(Page(nomination, params[0]))
    return pages
    
    


if __name__ == '__main__':
    main()
