from dataclasses import dataclass
import functools
import logging
import re

import mwparserfromhell
from pywikibot import Page, Category

logger = logging.getLogger("dyk_tools.article")

from dyk_tools.wiki.us_states import STATES


@functools.cache
def get_biography_infobox_templates(site) -> set[Page]:
    """Returns all the templates which represent people.

    This employs heuristics to navigate the infobox template categories.
    The exact rules are not well defined, so don't count on this returning
    exactly the same results every time.

    Because this is cached, a process restart or call to cache_clear()
    will be required to pick up any changes since the first invocation.
    Since these template categories change (very) slowly, that's not a
    problem in practice.

    """
    logger.debug("In get_biography_infobox_templates()")

    pages = set()
    cat = Category(site, "People and person infobox templates")
    ns = site.namespaces["Template"].id
    for t in cat.articles(recurse=3, namespaces=[ns]):
        if not t.title().endswith(" styles"):
            pages.add(t)
    pages.add(Page(site, "Template:Infobox character"))
    pages.add(Page(site, "Template:Infobox comics character"))
    return pages


@dataclass(frozen=True)
class Article:
    page: Page

    def title(self) -> str:
        return self.page.title()

    def url(self) -> str:
        return self.page.full_url()

    def is_biography(self) -> bool:
        return self.has_birth_category() or self.has_person_infobox()

    def has_birth_category(self) -> bool:
        for cat in self.page.categories():
            if cat.title().endswith(" births"):
                return True
        return False

    def has_person_infobox(self) -> bool:
        infoboxes = get_biography_infobox_templates(self.page.site)
        for t in self.page.templates():
            if t in infoboxes:
                return True
        return False

    def has_american_short_description(self) -> bool:
        wikicode = mwparserfromhell.parse(self.page.get())
        templates = wikicode.filter_templates(
            recursive=False, matches=lambda t: t.name.matches("short description")
        )
        if len(templates) == 0:
            return False
        if len(templates) > 1:
            logger.warning(
                "Found multiple {{short description}} templates in %s; using the first one",
                self.page.title,
            )
        template = templates[0]
        if len(template.params) == 0:
            logger.warning(
                "Found {{short description}} with no parameters in %s", self.page.title
            )
            return False
        text = template.params[0].value.lower()
        if "american" in text or "united states" in text:
            return True
        return False

    def is_american(self) -> bool:
        return self.american_in_first_sentence() or self.has_united_states_category()

    def american_in_first_sentence(self) -> bool:
        intro = self.page.extract(intro=True)
        sentences = re.split(r"[.?!] +[A-Z]", intro, maxsplit=1)
        first_sentence = sentences[0]
        return bool(re.search(r"(is|was) +an? +american", first_sentence.lower()))

    def has_united_states_category(self) -> bool:
        for cat in self.page.categories():
            if cat.title().lower().endswith(" in the united states"):
                return True
        return False

    def has_link_to_state(self) -> bool:
        linked_titles = {l.title() for l in self.page.linkedPages(namespaces=[""])}
        return bool(linked_titles & STATES)
