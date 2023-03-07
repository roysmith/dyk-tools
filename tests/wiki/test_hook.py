import pytest

from dyk_tools.wiki.hook import Hook


@pytest.fixture
def Page(mocker):
    return mocker.patch("dyk_tools.wiki.hook.Page", autospec=True)


@pytest.fixture
def Article(mocker):
    return mocker.patch("dyk_tools.wiki.hook.Article", autospec=True)


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
    @pytest.mark.parametrize(
        "input, result",
        [
            ("", ""),
            ("foo", "foo"),
            ("[[foo]]", '<a href="my url">foo</a>'),
            ("'''foo'''", "<b>foo</b>"),
            ("'''[[foo]]'''", '<b><a href="my url">foo</a></b>'),
            ("''italic''", "<i>italic</i>"),
            ("'''''[[foo]]'''''", '<i><b><a href="my url">foo</a></b></i>'),
            ("[[foo|bar]]", '<a href="my url">bar</a>'),
            ("foo&nbsp;bar", "foo&nbsp;bar"),
        ],
    )
    def test_returns_correct_string(self, site, Article, Page, input, result):
        Article(None).url.return_value = "my url"
        hook = Hook(input)
        assert hook.render(site) == result

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
    @pytest.mark.parametrize(
        "input, result",
        [
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
            ("'''[[Talk:Foo]]'''", ["Talk:Foo"]),
            ("'''[[Foo|Bar]]'''", ["Foo"]),
        ],
    )
    def test_finds_targets(self, site, input, result):
        site.expand_text.side_effect = lambda s: s
        hook = Hook(input)
        targets = hook.targets(site)
        assert list(targets) == result

    @pytest.mark.parametrize(
        "input, result",
        [
            ("'''{{HMS|Melpomene|1794|6}}'''", ["HMS Melpomene (1794)"]),
        ],
    )
    def test_expands_templates(self, site, input, result):
        site.expand_text.return_value = (
            "'''[[HMS Melpomene (1794)|HMS&nbsp;''Melpomene'']]'''"
        )

        hook = Hook(input)
        targets = hook.targets(site)
        l = list(targets)
        assert l == result
