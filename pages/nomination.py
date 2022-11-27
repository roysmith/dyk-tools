from dataclasses import dataclass

from pywikibot import Page


@dataclass(frozen=True)
class Nomination:
    page: Page

    def is_approved(self):
        for image in self.page.imagelinks():
            if image.title() == 'File:Symbol confirmed.svg':
                return True
        return False

    def articles(self):
        pages = []
        for t, params in self.page.templatesWithParams():
            if t.title == 'DYK nompage links':
                pages.append(Page(nomination, params[0]))
        return pages
