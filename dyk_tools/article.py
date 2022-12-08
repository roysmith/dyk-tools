from dataclasses import dataclass

from pywikibot import Page

@dataclass(frozen=True)
class Article:
    page: Page

    def is_biography(self) -> bool:
        for cat in self.page.categories():
            if cat.title().endswith(' births'):
                return True
        return False
        