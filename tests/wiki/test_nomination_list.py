from dataclasses import dataclass
from datetime import date
from textwrap import dedent
import typing

import pytest
import pywikibot
import mwparserfromhell as mwp

from dyk_tools import Nomination, NominationList, NominationListError


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
        """\
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


@pytest.mark.parametrize(
    "input_text, nom_title, expected_section_title, expected_text",
    [
        (
            """\
                ===Articles created/expanded on December 31===
                {{Template:Did you know nominations/Nom 1}}
                {{Template:Did you know nominations/Nom 2}}
                ===Articles created/expanded on January 15===
                {{Template:Did you know nominations/Nom 3}}
            """,
            "Template:Did you know nominations/Nom 1",
            "Articles created/expanded on December 31",
            """\
                ===Articles created/expanded on December 31===
                {{Template:Did you know nominations/Nom 2}}
                ===Articles created/expanded on January 15===
                {{Template:Did you know nominations/Nom 3}}
            """,
        ),
        (
            """\
                ===Articles created/expanded on April 1===
                {{Did you know nominations/Nom 1}}
                {{Did you know nominations/Nom 2}}
            """,
            "Template:Did you know nominations/Nom 1",
            "Articles created/expanded on April 1",
            """\
                ===Articles created/expanded on April 1===
                {{Did you know nominations/Nom 2}}
            """,
        ),
        (
            """\
                ===Articles created/expanded on February 1===
                {{Did you know nominations/Nom 1}}
                ===Articles created/expanded on February 2===
                {{Did you know nominations/Nom 2}}
            """,
            "Template:Did you know nominations/Nom 1",
            "Articles created/expanded on February 1",
            """\
                ===Articles created/expanded on February 2===
                {{Did you know nominations/Nom 2}}
            """,
        ),
    ],
)
def test_remove_nomination(
    mocker, site, page, input_text, nom_title, expected_section_title, expected_text
):
    page.get.return_value = dedent(input_text)
    mocker.patch("dyk_tools.wiki.nomination_list.Page", new=MockPage)
    nomlist = NominationList(page)
    old_nom_page = MockPage(site, nom_title)

    section = nomlist.remove_nomination(old_nom_page, "test message")

    nomlist.page.save.assert_called_once_with(summary="test message")
    assert section.title == expected_section_title
    assert section.level == 3
    assert nomlist.page.text == dedent(expected_text)


@pytest.mark.parametrize(
    "list_text, nom_title, message",
    [
        (
            """\
                ===Articles created/expanded on December 31===
            """,
            "Template:Foo",
            "'Template:Foo' is not a valid DYK nomination page title",
        ),
        (
            """\
                ===Articles created/expanded on December 31===
            """,
            "Template:Did you know nominations/Nom",
            "'Template:Did you know nominations/Nom' not found",
        ),
        (
            """\
                ==Articles created/expanded on December 31==
                {{Template:Did you know nominations/Nom}}
            """,
            "Template:Did you know nominations/Nom",
            "'Template:Did you know nominations/Nom' not in an L3 section",
        ),
        (
            """\
                {{Template:Did you know nominations/Nom}}
            """,
            "Template:Did you know nominations/Nom",
            "'Template:Did you know nominations/Nom' not in an L3 section",
        ),
        (
            """\
                ===Articles created/expanded on December 31===
                {{Template:Did you know nominations/Nom}}
                {{Template:Did you know nominations/Nom}}
            """,
            "Template:Did you know nominations/Nom",
            "'Template:Did you know nominations/Nom' has multiple transclusions",
        ),
        (
            """\
                ===Articles created/expanded on December 31===
                {{Template:Did you know nominations/Nom}}
                {{Did you know nominations/Nom}}
            """,
            "Template:Did you know nominations/Nom",
            "'Template:Did you know nominations/Nom' has multiple transclusions",
        ),
    ],
)
def test_remove_nomination_raises_on_errors(
    mocker, site, page, list_text, nom_title, message
):
    page.get.return_value = dedent(list_text)
    nomlist = NominationList(page)
    nom_page = MockPage(site, nom_title)

    with pytest.raises(NominationListError, match=message):
        nomlist.remove_nomination(nom_page, "")


@pytest.mark.parametrize(
    "input_text, nom_title, section_title, current_date, expected_text",
    [
        (
            """\
                ===Articles created/expanded on December 31===
                {{Did you know nominations/Nom 1}}
            """,
            "Did you know nominations/Nom 2",
            "Articles created/expanded on December 31",
            date(2023, 1, 1),
            """\
                ===Articles created/expanded on December 31===
                {{Did you know nominations/Nom 1}}
                {{Did you know nominations/Nom 2}}
            """,
        ),
        (
            """\
                ===Articles created/expanded on December 31===
                {{Did you know nominations/Nom 1}}
            """,
            "Did you know nominations/Nom 2",
            "Articles created/expanded on October 31",
            date(2023, 1, 1),
            """\
                ===Articles created/expanded on October 31===
                {{Did you know nominations/Nom 2}}
                ===Articles created/expanded on December 31===
                {{Did you know nominations/Nom 1}}
            """,
        ),
        (
            """\
                ===Articles created/expanded on December 31===
                {{Did you know nominations/Nom 1}}
            """,
            "Did you know nominations/Nom 2",
            "Articles created/expanded on October 31",
            date(2022, 11, 1),
            """\
                ===Articles created/expanded on December 31===
                {{Did you know nominations/Nom 1}}
                ===Articles created/expanded on October 31===
                {{Did you know nominations/Nom 2}}
            """,
        ),
    ],
)
def test_insert_nomination(
    mocker,
    site,
    page,
    input_text,
    nom_title,
    section_title,
    current_date,
    expected_text,
):
    page.get.return_value = dedent(input_text)
    mocker.patch("dyk_tools.wiki.nomination_list.Page", new=MockPage)
    _today = mocker.patch("dyk_tools.wiki.nomination_list._today", autospec=True)
    _today.return_value = current_date
    nomlist = NominationList(page)
    nom_page = MockPage(site, nom_title)
    heading = mwp.nodes.Heading(section_title, 3)
    nomlist.insert_nomination(nom_page, heading, "test message")

    nomlist.page.save.assert_called_once_with(summary="test message")
    assert nomlist.page.text == dedent(expected_text)


@pytest.mark.parametrize(
    "input, current_date, expected_result",
    [
        ("Articles created/expanded on March 24", date(2023, 4, 1), date(2023, 3, 24)),
        ("Articles created/expanded on march 24", date(2023, 4, 1), date(2023, 3, 24)),
        ("Articles created/expanded on July 1", date(2023, 4, 1), date(2022, 7, 1)),
        ("Articles created/expanded on April 1", date(2023, 4, 1), date(2023, 4, 1)),
    ],
)
def test_intuit_year_date(mocker, input, current_date, expected_result):
    _today = mocker.patch("dyk_tools.wiki.nomination_list._today", autospec=True)
    _today.return_value = current_date

    result = NominationList.intuit_year_date(input)

    assert result == expected_result


@pytest.mark.parametrize(
    "input_text, nom_title, expected_section_title",
    [
        (
            """\
                ===Articles created/expanded on December 31===
                {{Template:Did you know nominations/Nom 1}}
                {{Template:Did you know nominations/Nom 2}}
                ===Articles created/expanded on January 15===
                {{Template:Did you know nominations/Nom 3}}
            """,
            "Template:Did you know nominations/Nom 1",
            "Articles created/expanded on December 31",
        ),
        (
            """\
                ===Articles created/expanded on April 1===
                {{Did you know nominations/Nom 1}}
                {{Did you know nominations/Nom 2}}
            """,
            "Template:Did you know nominations/Nom 1",
            "Articles created/expanded on April 1",
        ),
        (
            """\
                ===Articles created/expanded on February 1===
                {{Did you know nominations/Nom 1}}
                ===Articles created/expanded on February 2===
                {{Did you know nominations/Nom 2}}
            """,
            "Template:Did you know nominations/Nom 1",
            "Articles created/expanded on February 1",
        ),
        (
            """\
                ===Articles created/expanded on February 1===
                {{Did you know nominations/Nom 1}}
                ===Articles created/expanded on February 2===
                {{Did you know nominations/Nom 2}}
            """,
            "Template:Did you know nominations/Nom 3",
            None,
        ),
    ],
)
def test_find_nomination(
    mocker, site, page, input_text, nom_title, expected_section_title
):
    page.get.return_value = dedent(input_text)
    mocker.patch("dyk_tools.wiki.nomination_list.Page", new=MockPage)
    nomlist = NominationList(page)
    old_nom_page = MockPage(site, nom_title)

    section = nomlist.find_nomination(old_nom_page)

    if expected_section_title is None:
        assert section is None
    else:
        heading = section.nodes[0]
        assert heading.title == expected_section_title
        assert heading.level == 3
