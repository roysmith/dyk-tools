from textwrap import dedent

from dyk_tools import Article

import pywikibot


class TestArticle:
    def test_article_can_be_constructed(self, page):
        article = Article(page)


class TestTitle:
    def test_title_returns_page_title(self, page):
        article = Article(page)
        page.title.return_value = "Foo"
        assert article.title() == "Foo"


class TestUrl:
    def test_url_returns_page_url(self, page):
        article = Article(page)
        page.full_url.return_value = "blah"
        assert article.url() == "blah"


class TestHasBirthCategory:
    def test_has_birth_category_returns_false_with_no_categories(self, page):
        article = Article(page)
        page.categories.return_value = []
        assert article.has_birth_category() == False

    def test_has_birth_category_returns_true_with_birth_category(self, mocker, page):
        article = Article(page)
        cat = mocker.Mock(spec=pywikibot.Category)
        cat.title.return_value = "1944 births"
        page.categories.return_value = [cat]
        assert article.has_birth_category() == True


class TestHasPersonInfobox:
    def test_has_person_infobox_returns_false_with_no_infobox(self, mocker, page):
        backend_mock_category_class = mocker.patch(
            "dyk_tools.article.Category", autospec=True
        )
        article = Article(page)
        page.templates.return_value = []
        assert article.has_person_infobox() == False

    def test_has_person_infobox_returns_true_with_correct_infobox(self, mocker, page):
        backend_mock_category_class = mocker.patch(
            "dyk_tools.article.Category", autospec=True
        )
        infobox_cat = backend_mock_category_class(None, None)
        infobox_cat.articles.return_value = [
            mocker.sentinel.infobox_engineer,
            mocker.sentinel.infobox_politician,
            mocker.sentinel.infobox_other,
        ]

        page.templates.return_value = [
            mocker.sentinel.infobox_engineer,
        ]

        mocker.resetall()
        article = Article(page)

        assert article.has_person_infobox() == True
        backend_mock_category_class.assert_called_once_with(
            page, "People and person infobox templates"
        )
        infobox_cat.articles.assert_called_once_with(recurse=1, namespaces=[mocker.ANY])

    def test_has_person_infobox_returns_false_with_unknown_infobox(self, mocker, page):
        backend_mock_category_class = mocker.patch(
            "dyk_tools.article.Category", autospec=True
        )
        infobox_cat = backend_mock_category_class(None, None)
        infobox_cat.articles.return_value = [
            mocker.sentinel.infobox_engineer,
            mocker.sentinel.infobox_politician,
            mocker.sentinel.infobox_other,
        ]

        page.templates.return_value = [
            mocker.sentinel.infobox_place,
        ]

        mocker.resetall()
        article = Article(page)

        assert article.has_person_infobox() == False
        backend_mock_category_class.assert_called_once_with(
            page, "People and person infobox templates"
        )
        infobox_cat.articles.assert_called_once_with(recurse=1, namespaces=[mocker.ANY])

    def test_has_american_short_description_returns_false_with_no_short_description(
        self, mocker, page
    ):
        page.get.return_value = ""
        article = Article(page)
        assert article.has_american_short_description() == False

    def test_has_american_short_description_returns_true_with_american(self, page):
        page.get.return_value = dedent(
            """\
            {{short description|An American thing}}
            """
        )
        article = Article(page)
        assert article.has_american_short_description() == True


class TestIsAmerican:
    def test_is_american_returns_false_with_blank_intro(self, page):
        page.extract.return_value = ""
        article = Article(page)
        assert article.is_american() == False

    def test_is_american_returns_true_with_is_an_american_in_first_sentence(self, page):
        page.extract.return_value = "Blah is an american thing"
        article = Article(page)
        assert article.is_american() == True

    def test_is_american_returns_false_with_south_american(self, page):
        page.extract.return_value = "Blah is a south american thing"
        article = Article(page)
        assert article.is_american() == False

    def test_is_american_returns_true_with_is_an_upper_case_american_in_first_sentence(
        self, page
    ):
        page.extract.return_value = "Blah is an American thing"
        article = Article(page)
        assert article.is_american() == True

    def test_is_american_returns_false_with_non_american_intro(self, page):
        page.extract.return_value = "I am british"
        article = Article(page)
        assert article.is_american() == False

    def test_is_american_returns_false_with_is_an_american_in_second_sentence(
        self, page
    ):
        page.extract.return_value = "Blah blah blah. And is an american too"
        article = Article(page)
        assert article.is_american() == False

    def test_is_american_returns_false_with_just_american_in_first_sentence(self, page):
        page.extract.return_value = "This is not an american thing."
        article = Article(page)
        assert article.is_american() == False

    def test_is_american_returns_true_with_united_states_category(self, mocker, page):
        cat = mocker.Mock(spec=pywikibot.Category)
        cat.title.return_value = "Things in the united states"
        page.categories.return_value = [cat]
        page.extract.return_value = ""
        article = Article(page)
        assert article.is_american() == True

    def test_is_american_returns_true_with_other_category(self, mocker, page):
        cat = mocker.Mock(spec=pywikibot.Category)
        cat.title.return_value = "Things in lower slobbovia"
        page.categories.return_value = [cat]
        page.extract.return_value = ""
        article = Article(page)
        assert article.is_american() == False
