from dyk_tools import Article

import pywikibot


def test_article_can_be_constructed(page):
    article = Article(page)


def test_has_birth_data_returns_false_with_no_categories(page):
    article = Article(page)
    page.categories.return_value = []
    assert article.is_biography() == False


def test_has_birth_data_returns_true_with_year_of_birth_category(mocker, page):
    article = Article(page)
    cat = mocker.Mock(spec=pywikibot.Category)
    cat.title.return_value = "1944 births"
    page.categories.return_value = [cat]
    assert article.is_biography() == True
