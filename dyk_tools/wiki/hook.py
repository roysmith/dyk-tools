from dataclasses import dataclass
import logging
from typing import Iterable

from mwparserfromhell import parse
from mwparserfromhell.nodes import Text, Wikilink, Tag, HTMLEntity
from mwparserfromhell.wikicode import Wikicode
from pywikibot import Site, Page

from .article import Article

logger = logging.getLogger("dyk_tools.hook")


@dataclass(frozen=True)
class Hook:
    text: str
    tag: str = ""

    def render(self, site: Site) -> str:
        wikicode = parse(self.text)
        return "".join(self._render_nodes(site, wikicode))

    def _render_nodes(self, site: Site, wikicode: Wikicode) -> Iterable[str]:
        for node in wikicode.nodes:
            if isinstance(node, Text):
                yield node.value
            elif isinstance(node, Wikilink):
                link = Article(Page(site, node.title)).url()
                text = str(node.text or node.title)
                yield f'<a href="{link}">{text}</a>'
            elif isinstance(node, Tag):
                yield f"<{node.tag}>{''.join(self._render_nodes(site, node.contents))}</{node.closing_tag}>"
            elif isinstance(node, HTMLEntity):
                yield str(node)
            else:
                logger.warning("Unknown node type (%s=%s)", type(node), node)

    def targets(self) -> Iterable[str]:
        """Iterates over the bolded links in a hook.  In theory, a hook must
        have at least one such hook, but nothing actually enforces that, so
        it's possible for this to return an empty iterator.

        Note that this returns the titles as strings, so:

          "'''[[Foo]]'''" => ["Foo"]
          "'''[[Foo#bar]]'''" => ["Foo#bar"]

        """
        wikicode = parse(self.text)
        for node in wikicode.filter_wikilinks():
            ancestors = wikicode.get_ancestors(node)
            if ancestors:
                outer = ancestors[-1]
                if isinstance(outer, Tag) and outer.tag == "b":
                    yield node.title
