from dataclasses import dataclass

from pywikibot import Page, Category

@dataclass(frozen=True)
class Article:
    page: Page

    def is_biography(self) -> bool:
        return self.has_birth_category() or self.has_person_infobox()


    def has_birth_category(self) -> bool:
        for cat in self.page.categories():
            if cat.title().endswith(' births'):
                return True
        return False


    def has_person_infobox(self) -> bool:
        category = Category(self.page, "People and person infobox templates")
        ns = self.page.site.namespaces['Template'].id
        infoboxes = list(category.articles(recurse=1, namespaces=[ns]))
        for t in self.page.templates():
            if t in infoboxes:
                return True
        return False


    def is_american(self) -> bool:
        return self.american_in_intro() or self.has_united_states_category()


    def american_in_intro(self) -> bool:
        intro = self.page.extract(intro=True).lower()
        return 'american' in intro


    def has_united_states_category(self) -> bool:
        for cat in self.page.categories():
            if cat.title().lower().endswith(' in the united states'):
                return True
        return False
