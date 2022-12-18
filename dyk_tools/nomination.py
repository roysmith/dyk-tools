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

    def is_previously_processed(self) -> bool:
        for t in self.page.itertemplates():
            if t.title() == "Template:DYK-Tools-Bot was here":
                return True
        return False

    def mark_processed(self, categories, categories_to_be_deleted) -> None:
        lines = self.page.get().split("\n")
        new_lines = []
        # This assumes categories are formatted one per line
        pattern = re.compile(r"\[\[([^]]*)\]\]$")
        for line in lines:
            m = pattern.match(line)
            if  m and m[1] in categories_to_be_deleted:
                continue
            if (
                "<!--Please do not write below this line or remove this line. Place comments above this line.-->"
                in line
            ):
                new_lines.append("{{Template:DYK-Tools-Bot was here}}")
                for cat in categories:
                       new_lines.append(f"[[{cat}]]")
            new_lines.append(line)
        self.page.text = "\n".join(new_lines)
        self.page.save("[[User:DYK-Tools-Bot|DYK-Tools-Bot]] classifying nomination.")
