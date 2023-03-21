from dataclasses import dataclass
from unittest.mock import Mock, MagicMock
import pytest
import pywikibot
import typing

from dyk_tools import Article
import dyk_tools.wiki.article


@pytest.fixture(autouse=True)
def MockCategory(mocker):
    return mocker.patch("dyk_tools.wiki.article.Category", autospec=True)


@pytest.fixture(autouse=True)
def clear_cache():
    dyk_tools.wiki.article.get_biography_infobox_templates.cache_clear()


@dataclass()
class MockPage:
    source: typing.Any
    _title: str

    def __post_init__(self):
        self.get = Mock()
        self.extract = Mock()
        self.categories = Mock(return_value=[])

    def title(self):
        return self._title


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


class TestArticle:
    def test_article_can_be_constructed(self, make_page):
        article = Article(make_page("Page 1"))


class TestTitle:
    def test_title_returns_page_title(self, make_page):
        article = Article(make_page("Foo"))
        assert article.title() == "Foo"


class TestUrl:
    def test_url_returns_page_url(self, make_page):
        page = make_page("Page 1")
        page.full_url.return_value = "blah"
        article = Article(page)
        assert article.url() == "blah"


class TestHasBirthCategory:
    def test_has_birth_category_returns_false_with_no_categories(self, make_page):
        page = make_page("Page 1")
        page.categories.return_value = []
        article = Article(page)
        assert article.has_birth_category() == False

    def test_has_birth_category_returns_true_with_birth_category(
        self, make_page, MockCategory
    ):
        cat = MockCategory(None, None)
        cat.title.return_value = "1944 births"
        page = make_page("Page 1")
        page.categories.return_value = [cat]
        article = Article(page)

        assert article.has_birth_category() == True


class TestHasPersonInfobox:
    # _params is a list of (result, article_templates, category_templates)
    # tuples.  Article_templates are the templates which will be returned
    # by article.templates().  Category_templates will be returned by
    # Category(site, "People and person infobox templates").articles().
    # Result is what Article.has_person_infobox() should return for that
    # combination.
    # fmt: off
    _params = [
        (False, [], []),
        (False, ["Template:Infobox A"], ["Template:Infobox B"]),
        (False, [], ["Template:Infobox A"]),
        (False, ["Template:Infobox C"], ["Template:Infobox A", "Template:Infobox B"]),
        (False, ["Template:Infobox archbishop styles"], ["Template:Infobox archbishop styles"]),
        (True, ["Template:Infobox A"], ["Template:Infobox A"]),
        (True, ["Template:Infobox A"], ["Template:Infobox A", "Template:Infobox B"]),
        (True, ["Template:Infobox A", "Template:Infobox B"], ["Template:Infobox B", "Template:Infobox C"]),
        (True, ["Template:Infobox character"], []),
        (True, ["Template:Infobox comics character"], []),
    ]
    # fmt: on

    @pytest.fixture()
    def MockCharacterPages(self, mocker, make_page):
        mock = mocker.patch("dyk_tools.wiki.article.Page", autospec=True)
        mock.__eq__ = lambda o1, o2: o1.title() == o2.title()
        mock.__hash__ = lambda o: hash(o.title())
        mock.side_effect = [
            make_page("Template:Infobox character"),
            make_page("Template:Infobox comics character"),
        ]
        return mock

    @pytest.fixture(params=_params)
    def result_templates(self, request):
        return request.param

    def test_has_person_infobox(
        self, mocker, result_templates, make_page, MockCategory, MockCharacterPages
    ):
        result, article_templates, category_templates = result_templates
        article_page = make_page("Article")
        article_page.templates.return_value = [make_page(t) for t in article_templates]
        infobox_cat = MockCategory(None, None)
        infobox_cat.articles.return_value = [make_page(t) for t in category_templates]
        mocker.resetall()
        article = Article(article_page)

        assert article.has_person_infobox() == result

        MockCategory.assert_called_once_with(
            article_page.site, "People and person infobox templates"
        )


class TestIsAmerican:
    @pytest.mark.parametrize(
        "text, expected_result",
        [
            ("", False),
            ("short description|An American thing", False),
            ("{{short description|An American thing}}", True),
        ],
    )
    def test_american_short_description(self, site, text, expected_result):
        page = MockPage(site, "Test page")
        page.get.return_value = text
        article = Article(page)

        result = article.has_american_short_description()

        assert result == expected_result

    @pytest.mark.parametrize(
        "text, expected_result",
        [
            ("", False),
            ("Blah is an american thing", True),
            ("Blah is a south american thing", False),
            ("Blah is an American thing", True),
            ("I am british", False),
            ("Blah blah blah. And is an american too", False),
            ("This is not an american thing.", False),
        ],
    )
    def test_american_short_description(self, site, text, expected_result):
        page = MockPage(site, "Test page")
        page.extract.return_value = text
        article = Article(page)

        result = article.is_american()

        assert result == expected_result

    @pytest.mark.parametrize(
        "category_title, expected_result",
        [("Things in the united states", True), ("Things in lower slobbovia", False)],
    )
    def test_american_category(
        self, site, MockCategory, category_title, expected_result
    ):
        page = MockPage(site, "Test page")
        cat = MockCategory(None, None)
        cat.title.return_value = category_title
        page.categories.return_value = [cat]
        page.extract.return_value = ""
        article = Article(page)

        result = article.is_american()

        assert result == expected_result
