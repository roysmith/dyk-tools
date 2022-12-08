import pytest
import pywikibot

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


def test_nomination_can_be_constructed(page):
    nomination = Nomination(page)


def test_is_approved_returns_false_with_no_images(page):
    page.imagelinks.return_value = []
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_true_with_tick(page, dyk_tick):
    page.imagelinks.return_value = [dyk_tick]
    nomination = Nomination(page)
    assert nomination.is_approved() is True


def test_is_approved_returns_true_with_tick_agf(page, dyk_tick_agf):
    page.imagelinks.return_value = [dyk_tick_agf]
    nomination = Nomination(page)
    assert nomination.is_approved() is True


def test_is_approved_returns_false_with_query(page, dyk_query):
    page.imagelinks.return_value = [dyk_query]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_query_override(page, dyk_tick, dyk_query):
    page.imagelinks.return_value = [dyk_tick, dyk_query]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_query_no_override(page, dyk_tick, dyk_query_no):
    page.imagelinks.return_value = [dyk_tick, dyk_query_no]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_no_override(page, dyk_tick, dyk_no):
    page.imagelinks.return_value = [dyk_tick, dyk_no]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_again_override(page, dyk_tick, dyk_again):
    page.imagelinks.return_value = [dyk_tick, dyk_again]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_articles_with_no_links_returns_empty_list(page):
    page.templatesWithParams.return_value = []
    nomination = Nomination(page)
    assert nomination.articles() == []


def test_articles_with_one_link_returns_list_with_one_page(mocker, page):
    backend_mock_page_class = mocker.patch("dyk_tools.nomination.Page", autospec=True)
    mock_page = backend_mock_page_class(None, None)
    backend_mock_page_class.reset_mock()
    template = mocker.Mock(spec=pywikibot.Page)()
    template.title.return_value = 'Template:DYK nompage links'
    page.templatesWithParams.return_value = [(template, ['my article', 'nompage=foo'])]
    nomination = Nomination(page)
    result = nomination.articles()
    assert result == [mock_page]
    backend_mock_page_class.assert_called_once_with(mocker.ANY, "my article")


def test_hooks_returns_empty_list_with_blank_page(page):
    page.get.return_value = ""
    nomination = Nomination(page)
    assert nomination.hooks() == []


def test_hooks_returns_single_hook(page):
    page.get.return_value = """
        ... that this is a hook?"""
    nomination = Nomination(page)
    assert nomination.hooks() == [Hook("", "... that this is a hook?")]


def test_hooks_returns_tag_and_text(page):
    page.get.return_value = """
        '''ALT0''' ... that blah?
        """
    nomination = Nomination(page)
    assert nomination.hooks() == [Hook("ALT0", "... that blah?")]


def test_hooks_returns_tag_and_text_with_colon_after_tag(page):
    page.get.return_value = """
        '''ALT0''': ... that blah?
        """
    nomination = Nomination(page)
    assert nomination.hooks() == [Hook("ALT0", "... that blah?")]


def test_hooks_returns_multiple_hooks(page):
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
