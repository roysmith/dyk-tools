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
        ===Articles created/expanded on January 15===
        {{Template:Did you know nominations/Piri (singer)}}
        """
    )
    mocker.patch("dyk_tools.wiki.nomination_list.Page", new=MockPage)
    nomlist = NominationList(page)

    noms = list(nomlist.nominations())

    titles = [nom.title() for nom in noms]
    assert titles == [
        "Template:Did you know nominations/Del Riley (clerk)",
        "Template:Did you know nominations/Braxton Cook",
        "Template:Did you know nominations/Piri (singer)",
    ]


def test_remove_nomination(mocker, site, page):
    page.get.return_value = dedent(
        """
        ===Articles created/expanded on December 31===
        {{Template:Did you know nominations/Nom 1}}
        {{Template:Did you know nominations/Nom 2}}
        ===Articles created/expanded on January 15===
        {{Template:Did you know nominations/Nom 3}}
        """
    )
    mocker.patch("dyk_tools.wiki.nomination_list.Page", new=MockPage)
    nomlist = NominationList(page)
    old_nom_page = MockPage(site, "Template:Did you know nominations/Nom 1")

    count = nomlist.remove_nomination(old_nom_page, "test message")

    nomlist.page.save.assert_called_once_with(summary="test message")
    assert count == 1
    expected_text = dedent(
        """
        ===Articles created/expanded on December 31===
        {{Template:Did you know nominations/Nom 2}}
        ===Articles created/expanded on January 15===
        {{Template:Did you know nominations/Nom 3}}
        """
    )
    assert nomlist.page.text == expected_text


def test_remove_nomination_raises_on_invalid_template(mocker, site, page):
    nomlist = NominationList(page)
    old_nom_page = MockPage(site, "Template:Foo")

    with pytest.raises(ValueError, match="'Template:Foo' .* page title"):
        nomlist.remove_nomination(old_nom_page, "test message")
