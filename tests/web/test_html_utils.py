from collections import namedtuple

import pytest
from more_itertools import consume
import mwparserfromhell as mwp

from dyk_tools.web.html_utils import render_hook, _render_nodes


@pytest.fixture
def Page(mocker):
    return mocker.patch("dyk_tools.web.html_utils.Page", autospec=True)


@pytest.fixture
def Article(mocker):
    return mocker.patch("dyk_tools.web.html_utils.Article", autospec=True)


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
def testcase(request, Page, Article):
    Article(None).url.return_value = "my url"
    TestCase = namedtuple("TestCase", "input output")
    return TestCase(*request.param)


def test_render(mocker, testcase, app):
    with app.app_context() as context:
        context.g = mocker.Mock()
        assert render_hook(testcase.input) == testcase.output


def test__render_nodes_logs_on_unknown_node(mocker, app, caplog):
    wikicode = mocker.Mock(spec=mwp.wikicode)
    wikicode.nodes = [None]
    with app.app_context() as context:
        context.g = mocker.Mock()
        consume(_render_nodes(wikicode))
    assert "Unknown node type" in caplog.text


def test__render_nodes_does_not_log_with_no_unknown_node(mocker, app, caplog, Page):
    text = r"""that '''[[Edward B. Barry]]''' demerited "humming"?"""
    wikicode = mwp.parse(text)
    with app.app_context() as context:
        context.g = mocker.Mock()
        consume(_render_nodes(wikicode))
    assert "Unknown node type" not in caplog.text
