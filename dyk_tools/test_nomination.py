import pytest
from textwrap import dedent

import pywikibot
import mwparserfromhell as mwp


from dyk_tools import Nomination, Hook


def icon(mocker, name):
    svg = mocker.Mock(spec=pywikibot.FilePage)
    svg.title.return_value = f"File:{name}.svg"
    return svg


@pytest.fixture
def dyk_tick(mocker):
    return icon(mocker, "Symbol confirmed")


@pytest.fixture
def dyk_tick_agf(mocker):
    return icon(mocker, "Symbol voting keep")


@pytest.fixture
def dyk_query(mocker):
    return icon(mocker, "Symbol question")


@pytest.fixture
def dyk_query_no(mocker):
    return icon(mocker, "Symbol possible vote")


@pytest.fixture
def dyk_no(mocker):
    return icon(mocker, "Symbol delete vote")


@pytest.fixture
def dyk_again(mocker):
    return icon(mocker, "Symbol redirect vote 4")


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


class TestIsApproved:
    def test_is_approved_returns_false_with_no_images(self, page):
        page.imagelinks.return_value = []
        nomination = Nomination(page)
        assert nomination.is_approved() is False

    def test_is_approved_returns_true_with_tick(self, page, dyk_tick):
        page.imagelinks.return_value = [dyk_tick]
        nomination = Nomination(page)
        assert nomination.is_approved() is True

    def test_is_approved_returns_true_with_tick_agf(self, page, dyk_tick_agf):
        page.imagelinks.return_value = [dyk_tick_agf]
        nomination = Nomination(page)
        assert nomination.is_approved() is True

    def test_is_approved_returns_false_with_query(self, page, dyk_query):
        page.imagelinks.return_value = [dyk_query]
        nomination = Nomination(page)
        assert nomination.is_approved() is False

    def test_is_approved_returns_false_with_query_override(
        self, page, dyk_tick, dyk_query
    ):
        page.imagelinks.return_value = [dyk_tick, dyk_query]
        nomination = Nomination(page)
        assert nomination.is_approved() is False

    def test_is_approved_returns_false_with_query_no_override(
        self, page, dyk_tick, dyk_query_no
    ):
        page.imagelinks.return_value = [dyk_tick, dyk_query_no]
        nomination = Nomination(page)
        assert nomination.is_approved() is False

    def test_is_approved_returns_false_with_no_override(self, page, dyk_tick, dyk_no):
        page.imagelinks.return_value = [dyk_tick, dyk_no]
        nomination = Nomination(page)
        assert nomination.is_approved() is False

    def test_is_approved_returns_false_with_again_override(
        self, page, dyk_tick, dyk_again
    ):
        page.imagelinks.return_value = [dyk_tick, dyk_again]
        nomination = Nomination(page)
        assert nomination.is_approved() is False


class TestArticles:
    def test_articles_with_no_links_returns_empty_list(self, page):
        page.templatesWithParams.return_value = []
        nomination = Nomination(page)
        assert nomination.articles() == []

    def test_articles_with_one_link_returns_list_with_one_page(self, mocker, page):
        # Set up the Page mock for Nomination.articles() to create instances of
        backend_mock_page_class = mocker.patch(
            "dyk_tools.nomination.Page", autospec=True
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
        assert result == [backend_mock_page_class(None, None)]

    def test_articles_with_n_links_returns_list_with_n_pages(self, mocker, page):
        # Set up the Page mock for Nomination.articles() to create instances of
        backend_mock_page_class = mocker.patch(
            "dyk_tools.nomination.Page", autospec=True
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
            backend_mock_page_class(None, None),
            backend_mock_page_class(None, None),
            backend_mock_page_class(None, None),
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
        assert nomination.hooks() == [Hook("", "... that this is a hook?")]

    def test_hooks_returns_tag_and_text(self, page):
        page.get.return_value = """
            '''ALT0''' ... that blah?
            """
        nomination = Nomination(page)
        assert nomination.hooks() == [Hook("ALT0", "... that blah?")]

    def test_hooks_returns_tag_and_text_with_colon_after_tag(self, page):
        page.get.return_value = """
            '''ALT0''': ... that blah?
            """
        nomination = Nomination(page)
        assert nomination.hooks() == [Hook("ALT0", "... that blah?")]

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
            Hook("", "... that this is a hook?"),
            Hook("", "... that this is also a hook?"),
            Hook("ALT1", "... that foo?"),
        ]


class TestIsPreviouslyProcessed:
    def test_is_prevously_processed_returns_false_with_no_templates(self, page):
        page.itertemplates.return_value = []
        nomination = Nomination(page)
        assert nomination.is_previously_processed() == False

    def test_is_previously_processed_returns_true_with_existing_dyk_tools_bot_template(
        self, mocker, page
    ):
        template = mocker.Mock(spec=pywikibot.Page)()
        template.title.return_value = "Template:DYK-Tools-Bot was here"
        page.itertemplates.return_value = [template]
        nomination = Nomination(page)
        assert nomination.is_previously_processed() == True


class TestMarkProcessed:
    def test_mark_processed_adds_template_after_dyk_subpage(self, mocker, page):
        page.get.return_value = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}<!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        nomination = Nomination(page)
        nomination.mark_processed([], [])

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        nodes = wikicode.filter(
            recursive=False, matches=lambda n: not isinstance(n, mwp.nodes.Text)
        )
        assert nodes[0].name.matches("DYKsubpage")
        assert nodes[1].name.matches("DYK-Tools-Bot was here")
        assert isinstance(nodes[2], mwp.nodes.Comment)

    def test_mark_processed_adds_template_and_categories(self, mocker, page):
        page.get.return_value = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}<!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        nomination = Nomination(page)
        nomination.mark_processed(
            ["Category:Foo", "Category:Bar"], ["Category:Foo", "Category:Bar"]
        )

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        templates = wikicode.filter_templates(recursive=False)
        assert any(t.name.matches("DYK-Tools-Bot was here") for t in templates)

        links = wikicode.filter_wikilinks(recursive=False)
        assert any(l.title.matches("Category:Foo") for l in links)
        assert any(l.title.matches("Category:Bar") for l in links)

    def test_mark_processed_cleans_out_pre_existing_categories(self, mocker, page):
        page.get.return_value = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}
            [[Category:Baz]]
            [[Category:Foo]]
            [[Category:Other]]
            <!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        nomination = Nomination(page)
        nomination.mark_processed(
            [],
            ["Category:Foo", "Category:Bar", "Category:Baz"],
        )

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        links = wikicode.filter_wikilinks(recursive=False)
        assert len([l for l in links if l.title.matches("Category:Foo")]) == 0
        assert len([l for l in links if l.title.matches("Category:Baz")]) == 0
        assert len([l for l in links if l.title.matches("Category:Other")]) == 1

    def test_mark_processed_removes_and_adds_categories(self, mocker, page):
        page.get.return_value = dedent(
            """\
            {{DYKsubpage
            |blah, blah
            }}
            [[Category:Baz]]
            [[Category:Foo]]
            [[Category:Other]]
            <!--Please do not write below this line or remove this line. Place comments above this line.-->
            """
        )
        nomination = Nomination(page)
        nomination.mark_processed(
            ["Category:Foo", "Category:Bar"],
            ["Category:Foo", "Category:Bar", "Category:Baz"],
        )

        page.save.assert_called_once()
        wikicode = mwp.parse(page.text)
        links = wikicode.filter_wikilinks(recursive=False)
        assert len([l for l in links if l.title.matches("Category:Foo")]) == 1
        assert len([l for l in links if l.title.matches("Category:Bar")]) == 1
        assert len([l for l in links if l.title.matches("Category:Baz")]) == 0
        assert len([l for l in links if l.title.matches("Category:Other")]) == 1

    def test_mark_processed_raises_value_error_with_unmanaged_category(self, page):
        nomination = Nomination(page)
        with pytest.raises(ValueError) as info:
            nomination.mark_processed(["Category:Foo"], ["Category:Bar"])
        info.match(r"{'Category:Foo'} not in managed_categories")
