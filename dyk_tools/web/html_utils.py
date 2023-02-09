from typing import Iterable

from flask import g, current_app
import mwparserfromhell as mwp
from pywikibot import Page


from dyk_tools import Article


def render_hook(wikitext: str) -> str:
    wikicode = mwp.parse(wikitext)
    return "".join(_render_nodes(wikicode))


def _render_nodes(wikicode: mwp.wikicode.Wikicode) -> Iterable[str]:
    for node in wikicode.nodes:
        if isinstance(node, mwp.nodes.Text):
            yield node.value
        elif isinstance(node, mwp.nodes.Wikilink):
            link = Article(Page(g.site, node.title)).url()
            text = str(node.text or node.title)
            yield f'<a href="{link}">{text}</a>'
        elif isinstance(node, mwp.nodes.Tag):
            yield f"<{node.tag}>{''.join(_render_nodes(node.contents))}</{node.closing_tag}>"
        elif isinstance(node, mwp.nodes.HTMLEntity):
            yield str(node)
        else:
            current_app.logger.warning(
                "Unknown node type (%s=%s) in render_hook()", type(node), node
            )
