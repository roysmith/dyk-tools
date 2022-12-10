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


def test_is_american_returns_false_with_blank_intro(page):
    page.extract.return_value = ""
    article = Article(page)
    assert article.is_american() == False


def test_is_american_returns_true_with_american_in_intro(page):
    page.extract.return_value = "Blah is an american thing"
    article = Article(page)
    assert article.is_american() == True


def test_is_american_returns_true_with_upper_case_american_in_intro(page):
    page.extract.return_value = "Blah is an American thing"
    article = Article(page)
    assert article.is_american() == True


def test_is_american_returns_false_with_non_american_intro(page):
    page.extract.return_value = "I am british"
    article = Article(page)
    assert article.is_american() == False


def test_is_american_returns_true_with_united_states_category(mocker, page):
    cat = mocker.Mock(spec=pywikibot.Category)
    cat.title.return_value = "Things in the united states"
    page.categories.return_value = [cat]
    article = Article(page)
    assert article.is_american() == True


def test_is_american_returns_true_with_other_category(mocker, page):
    cat = mocker.Mock(spec=pywikibot.Category)
    cat.title.return_value = "Things in lower slobbovia"
    page.categories.return_value = [cat]
    article = Article(page)
    assert article.is_american() == False


def test_is_american_returns_true_with_link_to_state_article(mocker, page):
    vermont = mocker.Mock(spec=pywikibot.Page)()
    vermont.title.return_value = "Vermont"
    page.linkedPages.return_value = [vermont]
    article = Article(page)
    assert article.is_american() == True
