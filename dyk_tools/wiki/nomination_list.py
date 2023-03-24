from dataclasses import dataclass
from enum import Enum, auto

from pywikibot import Page
from mwparserfromhell import parse
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Heading, Template, Text

from .nomination import Nomination


class NominationListError(RuntimeError):
    pass


@dataclass(frozen=True)
class NominationList:
    page: Page

    def nominations(self) -> list[Nomination]:
        wikicode = parse(self.page.get())
        for t in wikicode.filter_templates(
            recursive=False, matches="template:did you know nominations/"
        ):
            yield Nomination(Page(self.page, t.name))

    def remove_nomination(self, nomination: Page, message: str) -> int:
        """Remove a nomination transclusion and save the NominationList
        back to the wiki, using ''message'' as the edit summary.

        Returns the Heading node for the section where the title was found.

        Raises NominationListError if any of:
          * Nomination.title() doesn't look like a legitimate DYK nomination
          * Nomination isn't found in the list
          * Nomination is transcluded more than once
          * The list is incorrectly structured

        Note that nomination.title() must include the "Template:" namespace, but
        transclusions in the NominationList are recognized with or without
        the leading "Template:".

        """
        title = nomination.title()
        if not title.lower().startswith("template:did you know nominations/"):
            raise NominationListError(
                f"'{title}' is not a valid DYK nomination page title"
            )
        wikicode = parse(self.page.get())
        heading = self._remove_transclusion(title, wikicode)
        self.page.text = str(wikicode)
        self.page.save(summary=message)
        return heading

    def _remove_transclusion(self, title: str, wikicode: Wikicode) -> Heading:
        """Remove the transcluded title from the wikicode, which is mutated
        in-place.  Returns the Heading node for the section where the title
        was found.

        Keeping track of the state is really messy.  It would be nice if this
        could be simplified.

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

        # Derived from mwparserfromhell's Wikicode.matches()
        normalize = (
            lambda s: (s[0].upper() + s[1:]).replace("_", " ").removeprefix("Template:")
            if s
            else s
        )

        count = 0
        current_heading_node = None
        heading_node = None
        state = State.START
        nodes_to_remove = []
        base_title = normalize(title)
        for node in wikicode.ifilter(recursive=False):
            if isinstance(node, Heading):
                current_heading_node = node
                state = State.START
            elif isinstance(node, Text) and node.value == "\n":
                if state == State.TEMPLATE:
                    nodes_to_remove.append(node)
                state = State.NEWLINE
            elif isinstance(node, Template) and normalize(node.name) == base_title:
                if current_heading_node and current_heading_node.level == 3:
                    state = State.TEMPLATE if state == State.NEWLINE else State.START
                    nodes_to_remove.append(node)
                    if heading_node is None:
                        heading_node = current_heading_node
                    count += 1
                else:
                    raise NominationListError(f"'{title}' not in an L3 section")
            else:
                state = State.START
        if count == 0:
            raise NominationListError(f"'{title}' not found")
        if count > 1:
            raise NominationListError(f"'{title}' has multiple transclusions")
        for node in nodes_to_remove:
            wikicode.remove(node)
        return heading_node
