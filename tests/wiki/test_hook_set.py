import pytest
from textwrap import dedent

import pywikibot
import mwparserfromhell as mwp

from dyk_tools import HookSet


@pytest.fixture
def make_page(mocker, site):
    def _make_page(title):
        attrs = {
            "site": site,
            "title.return_value": title,
            "__eq__": lambda o1, o2: o1.title() == o2.title(),
            "__hash__": lambda o: hash(o.title()),
        }
        return mocker.MagicMock(spec=pywikibot.Page, **attrs)

    return _make_page


class TestNomination:
    def test_can_be_constructed(self, make_page):
        hook_set = HookSet(make_page("foo"))

    def test_title(self, make_page):
        hook_set = HookSet(make_page("foo"))
        assert hook_set.title() == "foo"

    def test_url(self, make_page):
        page = make_page("Page 1")
        page.full_url.return_value = "blah"
        hook_set = HookSet(page)
        assert hook_set.url() == "blah"


class TestHooks:
    def test_no_hooks(self, page):
        page.text = dedent(
            """
            <!--Hooks-->
            <!--HooksEnd-->
            """
        )
        hook_set = HookSet(page)
        assert list(hook_set.hooks()) == []

    def test_has_hooks_and_image(self, page):
        page.text = dedent(
            """
            <!--Hooks-->
            {{main page image/DYK|whatever}}
            * ... that foo?
            * ... that bar?
            * ...
            <!--HooksEnd-->
            """
        )
        hook_set = HookSet(page)
        hooks = list(hook_set.hooks())
        assert len(hooks) == 3


class TestTargets:
    def test_with_no_hooks_returns_no_targets(self, page):
        page.text = dedent(
            """
            <!--Hooks-->
            <!--HooksEnd-->
            """
        )
        hook_set = HookSet(page)
        targets = list(hook_set.targets())
        assert targets == []

    def test_with_mutiple_hooks__returns_targets(self, page):
        page.text = dedent(
            """
            <!--Hooks-->
            * ... that '''[[foo]]''' and '''[[bar]]'''?
            * ... that '''[[baz|display]]'''?
            * ... that there's no targets in this one
            <!--HooksEnd-->
            """
        )
        hook_set = HookSet(page)
        targets = list(hook_set.targets())
        assert targets == ["foo", "bar", "baz"]
