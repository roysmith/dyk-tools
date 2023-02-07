from collections import namedtuple

import pytest

from dyk_web.html_utils import render_hook


@pytest.fixture
def Page(mocker):
    return mocker.patch("dyk_web.html_utils.Page", autospec=True)


@pytest.fixture
def Article(mocker):
    return mocker.patch("dyk_web.html_utils.Article", autospec=True)


@pytest.fixture
def g(mocker, app):
    with app.app_context() as context:
        context.g = mocker.Mock()
        return mocker.patch("dyk_web.html_utils.g")


@pytest.fixture(
    params=[
        ("", ""),
        ("foo", "foo"),
        ("[[foo]]", '<a href="my url">foo</a>'),
        ("'''foo'''", "<b>foo</b>"),
        ("'''[[foo]]'''", '<b><a href="my url">foo</a></b>'),
        ("''italic''", "<i>italic</i>"),
        ("'''''[[foo]]'''''", '<i><b><a href="my url">foo</a></b></i>'),
        ("[[foo|bar]]", '<a href="my url">bar</a>'),
        ("foo&nbsp;bar", "foo&nbsp;bar"),
    ]
)
def testcase(request, Page, Article, g):
    Article(None).url.return_value = "my url"
    TestCase = namedtuple("TestCase", "input output")
    return TestCase(*request.param)


def test_render(testcase):
    assert render_hook(testcase.input) == testcase.output
