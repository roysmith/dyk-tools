from dataclasses import dataclass
import re

from pywikibot import Page, Category

from dyk_tools.us_states import STATES


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
        category = Category(self.page, "People and person infobox templates")
        ns = self.page.site.namespaces["Template"].id
        infoboxes = list(category.articles(recurse=1, namespaces=[ns]))
        for t in self.page.templates():
            if t in infoboxes:
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
