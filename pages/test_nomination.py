import pytest
import pytest_socket
import pywikibot

from nomination import Nomination


@pytest.fixture
def site(monkeypatch, mocker):
    """Returns a mock pywikibot.Site instance.  Also closes off some possible
    network leakage paths in case something bypasses the mock.

    """
    pytest_socket.disable_socket()
    monkeypatch.setattr(pywikibot.config, "max_retries", 0)
    mock_Site = mocker.patch("pywikibot.Site", autoconfig=pywikibot.site.APISite)
    return mock_Site()


@pytest.fixture
def Page(mocker):
    """Returns a mock of the pywikibot.Page class."""
    return mocker.patch("pywikibot.Page", autospec=True)


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


def test_nomination_can_be_constructed(site, Page):
    page = Page(site, "")
    nomination = Nomination(page)


def test_is_approved_returns_false_with_no_images(site, Page):
    page = Page(site, "")
    page.imagelinks.return_value = []
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_true_with_tick(site, Page, dyk_tick):
    page = Page(site, "")
    page.imagelinks.return_value = [dyk_tick]
    nomination = Nomination(page)
    assert nomination.is_approved() is True


def test_is_approved_returns_true_with_tick_agf(site, Page, dyk_tick_agf):
    page = Page(site, "")
    page.imagelinks.return_value = [dyk_tick_agf]
    nomination = Nomination(page)
    assert nomination.is_approved() is True


def test_is_approved_returns_false_with_query(site, Page, dyk_query):
    page = Page(site, "")
    page.imagelinks.return_value = [dyk_query]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_quey_override(site, Page, dyk_tick, dyk_query):
    page = Page(site, "")
    page.imagelinks.return_value = [dyk_tick, dyk_query]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_query_no_override(site, Page, dyk_tick, dyk_query_no):
    page = Page(site, "")
    page.imagelinks.return_value = [dyk_tick, dyk_query_no]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_no_override(site, Page, dyk_tick, dyk_no):
    page = Page(site, "")
    page.imagelinks.return_value = [dyk_tick, dyk_no]
    nomination = Nomination(page)
    assert nomination.is_approved() is False


def test_is_approved_returns_false_with_quey_override(site, Page, dyk_tick, dyk_again):
    page = Page(site, "")
    page.imagelinks.return_value = [dyk_tick, dyk_again]
    nomination = Nomination(page)
    assert nomination.is_approved() is False
