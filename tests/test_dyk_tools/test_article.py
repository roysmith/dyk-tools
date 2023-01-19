import pytest
import pywikibot
from dyk_tools import Article
import dyk_tools.article


@pytest.fixture(autouse=True)
def MockCategory(mocker):
    return mocker.patch("dyk_tools.article.Category", autospec=True)


@pytest.fixture(autouse=True)
def clear_cache():
    dyk_tools.article.get_biography_infobox_templates.cache_clear()


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

    def test_has_birth_category_returns_true_with_birth_category(self, make_page, cat1):
        page = make_page("Page 1")
        page.categories.return_value = [cat1]
        article = Article(page)
        cat1.title.return_value = "1944 births"
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
        mock = mocker.patch("dyk_tools.article.Page", autospec=True)
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
    def test_has_american_short_description_returns_false_with_no_short_description(
        self, page1
    ):
        page1.get.return_value = ""
        article = Article(page1)
        assert article.has_american_short_description() == False

    def test_has_american_short_description_returns_true_with_american(self, page1):
        page1.get.return_value = """
            {{short description|An American thing}}
            """
        article = Article(page1)
        assert article.has_american_short_description() == True

    def test_is_american_returns_false_with_blank_intro(self, page1):
        page1.extract.return_value = ""
        article = Article(page1)
        assert article.is_american() == False

    def test_is_american_returns_true_with_is_an_american_in_first_sentence(
        self, page1
    ):
        page1.extract.return_value = "Blah is an american thing"
        article = Article(page1)
        assert article.is_american() == True

    def test_is_american_returns_false_with_south_american(self, page1):
        page1.extract.return_value = "Blah is a south american thing"
        article = Article(page1)
        assert article.is_american() == False

    def test_is_american_returns_true_with_is_an_upper_case_american_in_first_sentence(
        self, page1
    ):
        page1.extract.return_value = "Blah is an American thing"
        article = Article(page1)
        assert article.is_american() == True

    def test_is_american_returns_false_with_non_american_intro(self, page1):
        page1.extract.return_value = "I am british"
        article = Article(page1)
        assert article.is_american() == False

    def test_is_american_returns_false_with_is_an_american_in_second_sentence(
        self, page1
    ):
        page1.extract.return_value = "Blah blah blah. And is an american too"
        article = Article(page1)
        assert article.is_american() == False

    def test_is_american_returns_false_with_just_american_in_first_sentence(
        self, page1
    ):
        page1.extract.return_value = "This is not an american thing."
        article = Article(page1)
        assert article.is_american() == False

    def test_is_american_returns_true_with_united_states_category(
        self, MockCategory, page1
    ):
        cat = MockCategory(None, None)
        cat.title.return_value = "Things in the united states"
        page1.categories.return_value = [cat]
        page1.extract.return_value = ""
        article = Article(page1)
        assert article.is_american() == True

    def test_is_american_returns_true_with_other_category(self, MockCategory, page1):
        cat = MockCategory(None, None)
        cat.title.return_value = "Things in lower slobbovia"
        page1.categories.return_value = [cat]
        page1.extract.return_value = ""
        article = Article(page1)
        assert article.is_american() == False
