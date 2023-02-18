from dataclasses import dataclass
import re
from typing import List

from pywikibot import Page
import mwparserfromhell as mwp

from .article import Article
from .hook import Hook

APPROVALS = ["File:Symbol confirmed.svg", "File:Symbol voting keep.svg"]
DISAPPROVALS = [
    "File:Symbol question.svg",
    "File:Symbol possible vote.svg",
    "File:Symbol delete vote.svg",
    "File:Symbol redirect vote 4.svg",
]


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

    def articles(self) -> List[Article]:
        articles = []
        for t, params in self.page.templatesWithParams():
            if t.title() == "Template:DYK nompage links":
                for param in params:
                    if "=" not in param:
                        articles.append(Article(Page(self.page.site, param)))
        return articles

    def hooks(self) -> list[Hook]:
        """Get the hooks from the nomination.

        Returns a list of Hook instances."""
        wikitext = self.page.get()
        pattern = re.compile(r"(?:'''(\w+)''':?)? *(\.\.\. that .*?\?)")
        return [Hook(tag, text) for tag, text in pattern.findall(wikitext)]

    def is_biography(self) -> bool:
        for article in self.articles():
            if article.is_biography():
                return True
        return False

    def is_american(self) -> bool:
        for article in self.articles():
            if article.is_american():
                return True
        return False

    def mark_processed(self, tags, managed_tags) -> None:
        unknown_tags = set(tags) - set(managed_tags)
        if unknown_tags:
            raise ValueError(f"{unknown_tags} not in managed_tags")

        wikicode = mwp.parse(self.page.get())
        for template in wikicode.filter_templates(recursive=False):
            for managed_tag in managed_tags:
                if template.name.matches(managed_tag):
                    wikicode.remove(template)

        for tag in tags:
            wikicode.append("\n{{%s}}" % tag)
        self.page.text = str(wikicode)
        self.page.save("[[User:DYK-Tools-Bot|DYK-Tools-Bot]] classifying nomination.")

    def clear_tags(self, tags) -> None:
        wikicode = mwp.parse(self.page.get())
        for template in wikicode.filter_templates(recursive=False):
            for tag in tags:
                if template.name.matches(tag):
                    wikicode.remove(template)
        self.page.text = str(wikicode)
        self.page.save("[[User:DYK-Tools-Bot|DYK-Tools-Bot]] clearing tags.")
