from dataclasses import dataclass

from pywikibot import Page
import mwparserfromhell as mwp

from .nomination import Nomination


@dataclass(frozen=True)
class NominationList:
    page: Page

    def nominations(self) -> list[Nomination]:
        wikicode = mwp.parse(self.page.get())
        for t in wikicode.filter_templates(
            recursive=False, matches="template:did you know nominations/"
        ):
            yield Nomination(Page(self.page, t.name))
