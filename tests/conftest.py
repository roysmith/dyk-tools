import pytest
import pytest_socket

import pywikibot


@pytest.fixture(autouse=True)
def site(monkeypatch, mocker):
    """Returns a mock pywikibot.APISite instance.

    Attempts to prevent accidental network traffic leaking from test by
    intercepting it at the Site and network levels.

    """
    pytest_socket.disable_socket()
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
def cat1(mocker):
    return mocker.MagicMock(spec=pywikibot.Category)()
