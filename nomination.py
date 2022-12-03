from dataclasses import dataclass

from pywikibot import Page

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

    def is_approved(self):
        state = False
        for image in self.page.imagelinks():
            if image.title() in APPROVALS:
                state = True
            if image.title() in DISAPPROVALS:
                state = False
        return state

    def articles(self):
        pages = []
        for t, params in self.page.templatesWithParams():
            if t.title == "DYK nompage links":
                pages.append(Page(self.page, params[0]))
        return pages
