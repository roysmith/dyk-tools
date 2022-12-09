#!/usr/bin/env python3

import argparse
import logging
import sys

from pywikibot import Site, Page
from dyk_tools import Article

logger = logging.getLogger('analyze_article')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('article',
                        help='Article title')
    parser.add_argument('--log-level',
                        choices=['debug', 'info', 'warning', 'error'],
                        default='info',
                        help='Set logging level')
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stderr, level=args.log_level.upper())

    site = Site('en', 'wikipedia')
    page = Page(site, args.article)
    article = Article(page)
    print(article)
    print(f"{article.has_birth_category()=}")
    print(f"{article.has_person_infobox()=}")
    print(f"{article.is_biography()=}")


if __name__ == '__main__':
    main()
