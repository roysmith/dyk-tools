from dataclasses import dataclass
import re
from typing import List

from pywikibot import Page
import mwparserfromhell as mwp

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

    def title(self) -> str:
        return self.page.title()

    def url(self) -> str:
        return self.page.full_url()

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

    def is_previously_processed(self) -> bool:
        for t in self.page.itertemplates():
            if t.title() == "Template:DYK-Tools-Bot was here":
                return True
        return False

    def mark_processed(self, categories, managed_categories) -> None:
        unknown_cats = set(categories) - set(managed_categories)
        if unknown_cats:
            raise ValueError(f"{unknown_cats} not in managed_categories")

        wikicode = mwp.parse(self.page.get())
        for cat_node in wikicode.filter_wikilinks(recursive=False):
            for managed_cat_title in managed_categories:
                if cat_node.title.matches(managed_cat_title):
                    wikicode.remove(cat_node)

        wikicode.append("\n{{DYK-Tools-Bot was here}}")
        for cat in categories:
            wikicode.append(f"\n[[{cat}]]")
        self.page.text = str(wikicode)
        self.page.save("[[User:DYK-Tools-Bot|DYK-Tools-Bot]] classifying nomination.")
