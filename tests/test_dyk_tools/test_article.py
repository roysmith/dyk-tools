import pytest
import pywikibot
from dyk_tools import Article
import dyk_tools.article


@pytest.fixture(autouse=True)
def MockPage(mocker):
    return mocker.patch("dyk_tools.article.Page", autospec=True)


@pytest.fixture(autouse=True)
def MockCategory(mocker):
    return mocker.patch("dyk_tools.article.Category", autospec=True)


@pytest.fixture(autouse=True)
def clear_cache():
    dyk_tools.article.get_biography_infobox_templates.cache_clear()


@pytest.fixture
def make_page(mocker, site):
    def _make_page(title):
        attrs = {"site": site, "title.return_value": title}
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
    def test_has_person_infobox_returns_false_with_no_infobox(self, make_page):
        page = make_page("Page 1")
        page.templates.return_value = []
        article = Article(page)
        assert article.has_person_infobox() == False

    def test_has_person_infobox_returns_true_with_correct_infobox(
        self, mocker, MockCategory, MockPage, make_page
    ):
        page1 = make_page("Foo")
        page2 = make_page("Template:Infobox A")
        page1.templates.return_value = [page2]
        infobox_cat = MockCategory(None, None)
        infobox_cat.articles.return_value = [page2]
        mocker.resetall()
        article = Article(page1)

        assert article.has_person_infobox() == True
        MockCategory.assert_called_once_with(
            page1.site, "People and person infobox templates"
        )
        infobox_cat.articles.assert_called_once_with(recurse=3, namespaces=[mocker.ANY])
        MockPage.assert_any_call(page1.site, "Template:Infobox character")
        MockPage.assert_any_call(page1.site, "Template:Infobox comics character")

    def test_has_person_infobox_returns_false_with_unknown_infobox(
        self, mocker, MockCategory, MockPage, make_page
    ):
        page1 = make_page("Article 1")
        page2 = make_page("Template:Foo")
        page3 = make_page("Article 2")
        page4 = make_page("Article 3")
        page1.templates.return_value = [page2]
        infobox_cat = MockCategory(None, None)
        infobox_cat.articles.return_value = [page3, page4]
        mocker.resetall()
        article = Article(page1)

        assert article.has_person_infobox() == False
        MockCategory.assert_called_once_with(
            page1.site, "People and person infobox templates"
        )
        infobox_cat.articles.assert_called_once_with(recurse=3, namespaces=[mocker.ANY])
        MockPage.assert_any_call(page1.site, "Template:Infobox character")
        MockPage.assert_any_call(page1.site, "Template:Infobox comics character")


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
        self, mocker, MockCategory, page1
    ):
        cat = MockCategory(None, None)
        cat.title.return_value = "Things in the united states"
        page1.categories.return_value = [cat]
        page1.extract.return_value = ""
        article = Article(page1)
        assert article.is_american() == True

    def test_is_american_returns_true_with_other_category(
        self, mocker, MockCategory, page1
    ):
        cat = MockCategory(None, None)
        cat.title.return_value = "Things in lower slobbovia"
        page1.categories.return_value = [cat]
        page1.extract.return_value = ""
        article = Article(page1)
        assert article.is_american() == False
