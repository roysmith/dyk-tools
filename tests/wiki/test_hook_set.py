import pytest
from textwrap import dedent

import pywikibot
import mwparserfromhell as mwp

from dyk_tools import Hook, HookSet


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


@pytest.fixture
def hook_set_page(mocker, site):
    """Returns a mock pywikibot.Page."""
    mock_Page = mocker.patch("dyk_tools.wiki.hook_set.Page", autospec=True)
    return mock_Page(site)


class TestHookSet:
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
            * ... that "where?" did '''[[Robert Peary]]''' explore?
            * ... that '''''[[The Immune]]''''' is a thriller?
            * ... that '''[[The Big Bang (1)|The Big Bang Theory]]'''{{-?}}
            * ...
            <!--HooksEnd-->
            """
        )
        hook_set = HookSet(page)
        hooks = set(hook_set.hooks())
        expected_hooks = set(
            [
                Hook(" that foo?"),
                Hook(" that bar?"),
                Hook(" that \"where?\" did '''[[Robert Peary]]''' explore?"),
                Hook(" that '''''[[The Immune]]''''' is a thriller?"),
                Hook(" that '''[[The Big Bang (1)|The Big Bang Theory]]'''{{-?}}"),
                Hook(""),
            ]
        )
        assert hooks == expected_hooks


class TestTargets:
    def test_with_no_hooks_returns_no_targets(self, site, page):
        page.text = dedent(
            """
            <!--Hooks-->
            <!--HooksEnd-->
            """
        )
        hook_set = HookSet(page)
        targets = list(hook_set.targets())
        assert targets == []

    def test_with_mutiple_hooks__returns_targets(self, mocker, page):
        mock_Page = mocker.patch("dyk_tools.wiki.hook_set.Page", autospec=True)
        page.text = dedent(
            """
            <!--Hooks-->
            * ... that '''[[foo]]''' and '''[[bar]]'''?
            * ... that '''[[baz|display]]'''?
            * ... that there's no targets in this one
            <!--HooksEnd-->
            """
        )
        page.site.expand_text.side_effect = lambda s: s
        hook_set = HookSet(page)

        targets = list(hook_set.targets())

        mock_Page.assert_has_calls(
            [
                mocker.call(page.site, "foo"),
                mocker.call(page.site, "bar"),
                mocker.call(page.site, "baz"),
            ]
        )
        assert len(targets) == 3


class TestPrepSequence:
    def test_returns_correct_sequence(self, site, hook_set_page):
        hook_set_page.extract.return_value = "3"
        assert list(HookSet.prep_sequence(site)) == [3, 4, 5, 6, 7, 1, 2]


class TestQueueSequence:
    def test_returns_correct_sequence(self, site, hook_set_page):
        hook_set_page.extract.return_value = "5"
        assert list(HookSet.queue_sequence(site)) == [5, 6, 7, 1, 2, 3, 4]
