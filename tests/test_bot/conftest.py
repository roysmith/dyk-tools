import pytest
import pytest_socket

import pywikibot


@pytest.fixture
def site(monkeypatch, mocker, autouse=True):
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
