import pytest
import pytest_socket

import pywikibot


def pytest_runtest_setup():
    pytest_socket.disable_socket()


@pytest.fixture
def site(monkeypatch, mocker):
    """Returns a mock pywikibot.Site instance."""
    monkeypatch.setattr(pywikibot.config, "max_retries", 0)
    mocker.patch(
        "pywikibot.Site",
        side_effect=RuntimeError("Don't call pywikibot.Site() in a unit test"),
    )
    return mocker.MagicMock(spec=pywikibot.site.APISite)


@pytest.fixture
def page(mocker, site):
    """Returns a mock pywikibot.Page."""
    mock_Page = mocker.patch("pywikibot.Page", autospec=True)
    return mock_Page(site)


@pytest.fixture
def page1(mocker, site):
    return mocker.MagicMock(spec=pywikibot.Page, site=site)


@pytest.fixture
def page2(mocker, site):
    return mocker.MagicMock(spec=pywikibot.Page, site=site)


@pytest.fixture
def page3(mocker, site):
    return mocker.MagicMock(spec=pywikibot.Page, site=site)


@pytest.fixture
def page4(mocker, site):
    return mocker.MagicMock(spec=pywikibot.Page, site=site)


@pytest.fixture
def cat1(mocker):
    return mocker.MagicMock(spec=pywikibot.Category)()
