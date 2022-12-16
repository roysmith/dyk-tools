from dataclasses import dataclass
import re
from typing import List

from pywikibot import Page

import dyk_tools

APPROVALS = ["File:Symbol confirmed.svg", "File:Symbol voting keep.svg"]
DISAPPROVALS = [
    "File:Symbol question.svg",
    "File:Symbol possible vote.svg",
    "File:Symbol delete vote.svg",
    "File:Symbol redirect vote 4.svg",
]


@dataclass(frozen=True)
class Hook:
    tag: str
    text: str


@dataclass(frozen=True)
class Nomination:
    page: Page

    def is_approved(self) -> bool:
        state = False
        for image in self.page.imagelinks():
            if image.title() in APPROVALS:
                state = True
            if image.title() in DISAPPROVALS:
                state = False
        return state

    def articles(self) -> List[Page]:
        pages = []
        for t, params in self.page.templatesWithParams():
            if t.title() == "Template:DYK nompage links":
                for param in params:
                    if "=" not in param:
                        pages.append(Page(self.page.site, param))
        return pages

    def hooks(self) -> list[Hook]:
        """Get the hooks from the nomination.

        Returns a list of Hook instances."""
        wikitext = self.page.get()
        pattern = re.compile(r"(?:'''(\w+)''':?)? *(\.\.\. that .*?\?)")
        return [Hook(tag, text) for tag, text in pattern.findall(wikitext)]

    def is_biography(self) -> bool:
        for page in self.articles():
            if dyk_tools.Article(page).is_biography():
                return True
        return False

    def is_american(self) -> bool:
        for page in self.articles():
            if dyk_tools.Article(page).is_american():
                return True
        return False
