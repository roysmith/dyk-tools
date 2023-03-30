from dataclasses import dataclass
import re
from typing import List

from pywikibot import Page
import mwparserfromhell as mwp
from mwparserfromhell.nodes import Template, Wikilink

from .article import Article
from .hook import Hook


APPROVALS = [
    "File:Symbol confirmed.svg",
    "File:Symbol voting keep.svg",
]
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
        """Return True if the last status indication is an approval.

        A checkmark icon counts as an approval.  Any of the other listed images count
        as a disapproval.  If there is a {{DYK checklist}} template, the status field
        is examined; a value of "y" counts as an approval; any other value
        counts as a disapproval.

        Traditionally, the icon's file link includes a trailing '|16px'.  Although some
        implementations require that, this does not.  It's unclear if that's the right
        thing, and may change in the future.

        """
        approved = False
        wikicode = mwp.parse(self.page.text)
        for node in wikicode.ifilter():
            if isinstance(node, Wikilink):
                if any(node.title.matches(t) for t in APPROVALS):
                    approved = True
                if any(node.title.matches(t) for t in DISAPPROVALS):
                    approved = False
            if isinstance(node, Template) and node.name.matches("DYK checklist"):
                if (
                    node.has("status")
                    and node.get("status").value.lower().strip() == "y"
                ):
                    approved = True
                else:
                    approved = False

        return approved

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
        # https://stackoverflow.com/questions/75502022
        pattern = re.compile(
            r"""(?:'''(\w+)''':?)?
            (?:\ *)
            (\.\.\.\ that\ .*?\?)""",
            flags=re.VERBOSE,
        )
        return [Hook(text, tag) for tag, text in pattern.findall(wikitext)]

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
        username = self.page.site.username()
        self.page.save(f"[[User:{username}|{username}]] classifying nomination.")

    def clear_tags(self, tags) -> None:
        wikicode = mwp.parse(self.page.get())
        for template in wikicode.filter_templates(recursive=False):
            for tag in tags:
                if template.name.matches(tag):
                    wikicode.remove(template)
        self.page.text = str(wikicode)
        username = self.page.site.username()
        self.page.save(f"[[User:{username}|{username}]] clearing tags.")
