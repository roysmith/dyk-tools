from collections import namedtuple

import pytest

from dyk_tools.wiki.hook import Hook


@pytest.fixture
def Page(mocker):
    return mocker.patch("dyk_tools.wiki.hook.Page", autospec=True)


@pytest.fixture
def Article(mocker):
    return mocker.patch("dyk_tools.wiki.hook.Article", autospec=True)


def test_construct():
    hook = Hook("tag", "text")
    assert hook.tag == "tag"
    assert hook.text == "text"


class TestRender:
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
    def testcase(self, request, Page, Article):
        Article(None).url.return_value = "my url"
        TestCase = namedtuple("TestCase", "input output")
        return TestCase(*request.param)

    def test_returns_correct_string(self, site, testcase):
        hook = Hook("", testcase.input)
        assert hook.render(site) == testcase.output

    def test_logs_on_unknown_node(self, mocker, site, caplog):
        parse = mocker.patch("dyk_tools.wiki.hook.parse", autospec=True)
        parse("").nodes = [None]
        hook = Hook(None, "")
        hook.render(site)
        assert "Unknown node type" in caplog.text

    def test_does_not_log_with_no_unknown_node(self, mocker, site, caplog, Page):
        hook = Hook("", r"that '''[[Edward B. Barry]]''' demerited 'humming'?")
        hook.render(site)
        assert "Unknown node type" not in caplog.text
