import pytest
import pytest_socket

import pywikibot


def pytest_runtest_setup():
    pytest_socket.disable_socket()


@pytest.fixture
def site(monkeypatch, mocker):
    """Returns a mock pywikibot.Site instance."""
    monkeypatch.setattr(pywikibot.config, "max_retries", 0)
    mock_Site = mocker.patch("pywikibot.Site", autoconfig=pywikibot.site.APISite)
    return mock_Site()


@pytest.fixture
def page(mocker, site):
    """Returns a mock pywikibot.Page."""
    mock_Page = mocker.patch("pywikibot.Page", autospec=True)
    return mock_Page(site)
