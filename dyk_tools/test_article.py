from dyk_tools import Article

import pywikibot


def test_article_can_be_constructed(page):
    article = Article(page)


def test_has_birth_category_returns_false_with_no_categories(page):
    article = Article(page)
    page.categories.return_value = []
    assert article.has_birth_category() == False


def test_has_birth_category_returns_true_with_birth_category(mocker, page):
    article = Article(page)
    cat = mocker.Mock(spec=pywikibot.Category)
    cat.title.return_value = "1944 births"
    page.categories.return_value = [cat]
    assert article.has_birth_category() == True


def test_has_person_infobox_returns_false_with_no_infobox(mocker, page):
    backend_mock_category_class = mocker.patch(
        "dyk_tools.article.Category", autospec=True
    )
    article = Article(page)
    page.templates.return_value = []
    assert article.has_person_infobox() == False


def test_has_person_infobox_returns_true_with_correct_infobox(mocker, page):
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


def test_has_person_infobox_returns_false_with_unknown_infobox(mocker, page):
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
