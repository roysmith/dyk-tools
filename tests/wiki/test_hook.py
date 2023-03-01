from collections import namedtuple

import pytest

from dyk_tools.wiki.hook import Hook


@pytest.fixture
def Page(mocker):
    return mocker.patch("dyk_tools.wiki.hook.Page", autospec=True)


@pytest.fixture
def Article(mocker):
    return mocker.patch("dyk_tools.wiki.hook.Article", autospec=True)


TCData = namedtuple("TCData", "input output")


class TestConstruct:
    def test_with_tag(self):
        hook = Hook("text", "tag")
        assert hook.text == "text"
        assert hook.tag == "tag"

    def test_no_tag(self):
        hook = Hook("text")
        assert hook.text == "text"
        assert hook.tag == ""


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
        return TCData(*request.param)

    def test_returns_correct_string(self, site, testcase):
        hook = Hook(testcase.input)
        assert hook.render(site) == testcase.output

    def test_logs_on_unknown_node(self, mocker, site, caplog):
        parse = mocker.patch("dyk_tools.wiki.hook.parse", autospec=True)
        parse("").nodes = [None]
        hook = Hook("")
        hook.render(site)
        assert "Unknown node type" in caplog.text

    def test_does_not_log_with_no_unknown_node(self, mocker, site, caplog, Page):
        hook = Hook(r"that '''[[Edward B. Barry]]''' demerited 'humming'?")
        hook.render(site)
        assert "Unknown node type" not in caplog.text


class TestTargets:
    @pytest.fixture(
        params=[
            ("'''[[Foo]]'''", ["Foo"]),
            ("", []),
            ("[[Foo]]", []),
            ("''[[Foo]]''", []),
            ("'''''[[Foo]]'''''", ["Foo"]),
            ("'''[external]'''", []),
            ("... that '''[[One]]''' and '''[[Two]]'''", ["One", "Two"]),
            ("'''[[Foo|Bar]]'''", ["Foo"]),
            ("x \"'''[[Playin' Fiddle]]'''\" x", ["Playin' Fiddle"]),
            ("the '''''[[Capitol]]'''''{{'s}} motto", ["Capitol"]),
            ("[[Article|'''pipe''']]", []),
            ("'''[[Article#section|pipe]]''',", ["Article#section"]),
            ("'''[[Art? icle]]'''", ["Art? icle"]),
        ]
    )
    def testcase(self, request):
        return TCData(*request.param)

    def test_finds_targets(self, site, testcase):
        hook = Hook(testcase.input)
        assert list(hook.targets()) == testcase.output
