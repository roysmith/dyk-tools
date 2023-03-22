from dataclasses import dataclass
from enum import Enum, auto

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

    def remove_nomination(self, old_page: Page, message: str) -> int:
        """Remove a nomination transclusion and save the NominationList
        back to the wiki, using ''message'' as the edit summary.

        Returns the number of transclusions which were removed.  The current
        implementation will remove all instances if old_page is transcluded more than
        once.  It's unclear if this is the desired behavior, and may change in the
        future.

        Raises ValueError if old_page.title() doesn't look like a legitimate
        DYK nomination template.

        """
        title = old_page.title()
        if not title.lower().startswith("template:did you know nominations/"):
            raise ValueError(f"'{title}' is not a valid DYK nomination page title")
        wikicode = mwp.parse(self.page.get())
        count = self._remove_transclusion(title, wikicode)
        self.page.text = str(wikicode)
        self.page.save(summary=message)
        return count

    def _remove_transclusion(self, title, wikicode):
        """Remove the transcluded title from the wikicode, which is
        mutated in-place.

        """

        class State(Enum):
            # If (as is the most common case) a deleted transclusion is by itself on a
            # line, we don't want to leave behind an empty line.  To handle this, we
            # maintain a small state machine which recognizes a "newline, template,
            # newline" sequence allowing us to delete the second newline.  We can't
            # mutate the wikicode while we're iterating through it, so we just keep
            # track of what nodes need to be deleted and delete them all in a second
            # pass.
            START = auto()
            NEWLINE = auto()
            TEMPLATE = auto()

        count = 0
        state = State.START
        nodes_to_remove = []
        for node in wikicode.ifilter(recursive=False):
            if isinstance(node, mwp.nodes.Text) and node.value == "\n":
                if state == State.TEMPLATE:
                    nodes_to_remove.append(node)
                state = State.NEWLINE
            elif isinstance(node, mwp.nodes.Template) and node.name.matches(title):
                state = State.TEMPLATE if state == State.NEWLINE else State.START
                nodes_to_remove.append(node)
                count += 1
            else:
                state = State.START
        for node in nodes_to_remove:
            wikicode.remove(node)
        return count
