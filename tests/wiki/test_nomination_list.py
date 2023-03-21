from dataclasses import dataclass
from textwrap import dedent
import typing

import pytest
import pywikibot

from dyk_tools import Nomination, NominationList


@dataclass(frozen=True)
class MockPage:
    source: typing.Any
    _title: str

    def title(self):
        return self._title


def test_construct(page):
    page.title.return_value = "Foo"
    nomlist = NominationList(page)
    assert nomlist.page.title() == "Foo"


def test_nominations(mocker, page):
    page.get.return_value = dedent(
        """
        ===Articles created/expanded on December 31===
        {{Template:Did you know nominations/Del Riley (clerk)}}
        {{Template:Did you know nominations/Braxton Cook}}
        {{Template:Did you know nominations/Niwar (cotton tape)}}
        ===Articles created/expanded on January 15===
        {{Template:Did you know nominations/Piri (singer)}}
        """
    )
    mocker.patch("dyk_tools.wiki.nomination_list.Page", new=MockPage)
    nomlist = NominationList(page)

    nom_generator = nomlist.nominations()

    noms = list(nom_generator)
    titles = [nom.title() for nom in noms]
    assert titles == [
        "Template:Did you know nominations/Del Riley (clerk)",
        "Template:Did you know nominations/Braxton Cook",
        "Template:Did you know nominations/Niwar (cotton tape)",
        "Template:Did you know nominations/Piri (singer)",
    ]
