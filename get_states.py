#!/usr/bin/env python3

import argparse
import logging
import sys

from pywikibot import Site, Page, Category
from dyk_tools import Article

logger = logging.getLogger('analyze_article')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level',
                        choices=['debug', 'info', 'warning', 'error'],
                        default='info',
                        help='Set logging level')
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stderr, level=args.log_level.upper())

    site = Site('en', 'wikipedia')
    cat = Category(site, "States of the United States")
    for article in cat.articles():
        print(article.title())


if __name__ == '__main__':
    main()
