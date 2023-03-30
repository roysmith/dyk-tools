import pytest
from textwrap import dedent
from unittest.mock import Mock, PropertyMock

import pywikibot
import mwparserfromhell as mwp


from dyk_tools import Article, Nomination, Hook


DYK_TICK = "[[File:Symbol confirmed.svg|16px]]"
DYK_TICK_AGF = "[[File:Symbol voting keep.svg|16px]]"
DYK_QUERY = "[[File:Symbol question.svg|16px]]"
DYK_QUERY_NO = "[[File:Symbol possible vote.svg|16px]]"
DYK_NO = "[[File:Symbol delete vote.svg|16px]]"
DYK_AGAIN = "[[File:Symbol redirect vote 4.svg|16px]]"

DYK_TICK_LOWER_CASE_FILE = "[[file:Symbol confirmed.svg|16px]]"
DYK_TICK_LOWER_CASE_SYMBOL = "[[File:symbol confirmed.svg|16px]]"


class TestNomination:
    def test_nomination_can_be_constructed(self, page):
        nomination = Nomination(page)


class TestTitle:
    def test_title_returns_page_title(self, page):
        nomination = Nomination(page)
        page.title.return_value = "Foo"
        assert nomination.title() == "Foo"


class TestUrl:
    def test_url_returns_page_url(self, page):
        nomination = Nomination(page)
        page.full_url.return_value = "blah"
        assert nomination.url() == "blah"


@pytest.mark.parametrize(
    "text, result",
    [
        ("", False),
        (f"{DYK_TICK}", True),
        (f"{DYK_TICK_AGF}", True),
        (f"{DYK_QUERY}", False),
        (f"{DYK_TICK}\n{DYK_QUERY}", False),
        (f"{DYK_TICK}\n{DYK_QUERY_NO}", False),
        (f"{DYK_TICK}\n{DYK_NO}", False),
        (f"{DYK_TICK}\n{DYK_AGAIN}", False),
        (f"{DYK_TICK_LOWER_CASE_FILE}", True),
        pytest.param(
            f"{DYK_TICK_LOWER_CASE_SYMBOL}",
            True,
            marks=pytest.mark.xfail(
                reason="https://github.com/earwig/mwparserfromhell/issues/302"
            ),
        ),
        (f"{{{{DYK checklist|status=y}}}}", True),
        (f"{{{{DYK checklist|status=y}}}}\n{DYK_TICK}", True),
        (f"{{{{DYK checklist|status=y}}}}\n{DYK_QUERY}", False),
        (f"{{{{DYK checklist|status=y}}}}\n{{{{DYK checklist|status=y}}}}", True),
        (f"{{{{DYK checklist|status=y}}}}\n{{{{DYK checklist|status=n}}}}", False),
        (f"{{{{DYK checklist|status=n}}}}\n{{{{DYK checklist|status=y}}}}", True),
    ],
)
def test_is_approved(page, text, result):
    type(page).text = PropertyMock(return_value=text)
    nomination = Nomination(page)
    assert nomination.is_approved() is result


class TestArticles:
    def test_articles_with_no_links_returns_empty_list(self, page):
        page.templatesWithParams.return_value = []
        nomination = Nomination(page)
        assert nomination.articles() == []

    def test_articles_with_one_link_returns_list_with_one_article(self, mocker, page):
        # Set up the Page mock for Nomination.articles() to create instances of
        backend_mock_page_class = mocker.patch(
            "dyk_tools.wiki.nomination.Page", autospec=True
        )

        # Set up the mock template for Nomination.articles() to examine
        template = mocker.Mock(spec=pywikibot.Page)()
        template.title.return_value = "Template:DYK nompage links"

        page.templatesWithParams.return_value = [
            (template, ["my article", "nompage=foo"])
        ]
        nomination = Nomination(page)

        result = nomination.articles()

        backend_mock_page_class.assert_called_once_with(mocker.ANY, "my article")
        assert result == [Article(backend_mock_page_class(None, None))]

    def test_articles_with_n_links_returns_list_with_n_articles(self, mocker, page):
        # Set up the Page mock for Nomination.articles() to create instances of
        backend_mock_page_class = mocker.patch(
            "dyk_tools.wiki.nomination.Page", autospec=True
        )

        # Set up the mock template for Nomination.articles() to examine
        template = mocker.Mock(spec=pywikibot.Page)()
        template.title.return_value = "Template:DYK nompage links"

        page.templatesWithParams.return_value = [
            (template, ["article 1", "article 2", "article 3", "nompage=foo"]),
        ]
        nomination = Nomination(page)

        result = nomination.articles()

        backend_mock_page_class.assert_has_calls(
            [
                mocker.call(mocker.ANY, "article 1"),
                mocker.call(mocker.ANY, "article 2"),
                mocker.call(mocker.ANY, "article 3"),
            ],
            any_order=True,
        )
        assert result == [
            Article(backend_mock_page_class(None, None)),
            Article(backend_mock_page_class(None, None)),
            Article(backend_mock_page_class(None, None)),
        ]


class TestHooks:
    def test_hooks_returns_empty_list_with_blank_page(self, page):
        page.get.return_value = ""
        nomination = Nomination(page)
        assert nomination.hooks() == []

    def test_hooks_returns_single_hook(self, page):
        page.get.return_value = """
            ... that this is a hook?"""
        nomination = Nomination(page)
        assert nomination.hooks() == [Hook("... that this is a hook?")]

    def test_hooks_returns_tag_and_text(self, page):
        page.get.return_value = """
            '''ALT0''' ... that blah?
            """
        nomination = Nomination(page)
        assert nomination.hooks() == [Hook("... that blah?", "ALT0")]

    def test_hooks_returns_tag_and_text_with_colon_after_tag(self, page):
        page.get.return_value = """
            '''ALT0''': ... that blah?
            """
        nomination = Nomination(page)
        assert nomination.hooks() == [Hook("... that blah?", "ALT0")]

    def test_hooks_returns_multiple_hooks(self, page):
        page.get.return_value = """
            blah, blah
            ... that this is a hook?
            ... not this one?
            ... that this is also a hook?
            '''ALT1''' ... that foo?
            """
        nomination = Nomination(page)
        assert nomination.hooks() == [
            Hook("... that this is a hook?"),
            Hook("... that this is also a hook?"),
            Hook("... that foo?", "ALT1"),
        ]


class TestMarkProcessed:
    def test_mark_processed_adds_categories(self, page):
        page.get.return_value = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}<!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        nomination = Nomination(page)
        nomination.mark_processed(["Foo", "Bar"], ["Foo", "Bar"])

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        templates = wikicode.filter_templates(recursive=False)
        template_names = {str(t.name) for t in templates}
        assert "Foo" in template_names
        assert "Bar" in template_names

    def test_mark_processed_cleans_out_pre_existing_categories(self, page):
        page.get.return_value = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}
            {{Baz}}
            {{Foo}}
            {{Other}}
            <!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        nomination = Nomination(page)
        nomination.mark_processed(
            [],
            ["Foo", "Bar", "Baz"],
        )

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        templates = wikicode.filter_templates(recursive=False)
        template_names = {str(t.name) for t in templates}
        assert "Foo" not in template_names
        assert "Baz" not in template_names
        assert "Other" in template_names

    def test_mark_processed_removes_and_adds_categories(self, page):
        page.get.return_value = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}
            {{Baz}}
            {{Foo}}
            {{Other}}
            <!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        nomination = Nomination(page)
        nomination.mark_processed(
            ["Foo", "Bar"],
            ["Foo", "Bar", "Baz"],
        )

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        templates = wikicode.filter_templates(recursive=False)
        template_names = {str(t.name) for t in templates}
        assert "Foo" in template_names
        assert "Bar" in template_names
        assert "Baz" not in template_names
        assert "Other" in template_names

    def test_mark_processed_raises_value_error_with_unmanaged_category(self, page):
        nomination = Nomination(page)
        with pytest.raises(ValueError) as info:
            nomination.mark_processed(["Foo"], ["Bar"])
        info.match(r"{'Foo'} not in managed_tags")

    def test_mark_processed_generates_correct_edit_summary(self, page):
        page.get.return_value = dedent(
            """
            {{DYKsubpage}}
            """
        )
        page.site.username.return_value = "Me"
        nomination = Nomination(page)

        nomination.mark_processed(["Foo"], ["Foo"])

        page.save.assert_called_once_with("[[User:Me|Me]] classifying nomination.")


class TestClearTags:
    def test_article_with_no_tags_is_unchanged(self, page):
        original_text = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}<!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        page.get.return_value = original_text
        nomination = Nomination(page)

        nomination.clear_tags(["Foo", "Bar"])

        page.save.assert_called_once()
        assert page.text == original_text

    def test_tags_in_article_are_deleted(self, page):
        original_text = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}<!--Please do not write below this line or remove this line. Place comments above this line.-->
            {{Foo}}
            {{Bar}}
            {{Baz}}
            """
        )
        page.get.return_value = original_text
        nomination = Nomination(page)

        nomination.clear_tags(["Foo", "Bar"])

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        templates = wikicode.filter_templates(recursive=False)
        template_names = {str(t.name) for t in templates}
        assert "Foo" not in template_names
        assert "Bar" not in template_names
        assert "Baz" in template_names

    def test_clear_tags_generates_correct_edit_summary(self, page):
        page.get.return_value = dedent(
            """
            {{DYKsubpage}}
            """
        )
        page.site.username.return_value = "Me"
        nomination = Nomination(page)

        nomination.clear_tags(["Foo"])

        page.save.assert_called_once_with("[[User:Me|Me]] clearing tags.")
