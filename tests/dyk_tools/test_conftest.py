"""This test is just paranoia about accidentally leaking network traffic."""

import requests
import pytest
from pytest_socket import SocketBlockedError


def test_sockets_are_disabled(site):
    with pytest.raises(SocketBlockedError):
        r = requests.get("https://en.wikipedia.org/")
        print(r.status_code)
