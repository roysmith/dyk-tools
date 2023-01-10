from textwrap import dedent

import dyk_tools
from dyk_web.api import API_Hook, API_Article, API_Nomination


class Test_API_Hook:
    def test_construction(self):
        api_hook = API_Hook("foo", "bar")
        assert api_hook.tag == "foo"
        assert api_hook.text == "bar"

    def test_from_hook(self):
        hook = dyk_tools.Hook("tag", "text")
        api_hook = API_Hook.from_hook(hook)
        assert api_hook == API_Hook("tag", "text")


class Test_API_Article:
    def test_construction(self):
        api_article = API_Article("Title", "url", True, False)
        assert api_article.title == "Title"
        assert api_article.url == "url"
        assert api_article.is_biography == True
        assert api_article.is_american == False

    def test_from_article(self, mocker):
        article = mocker.Mock(spec=dyk_tools.Article)
        article.title = "title"
        article.url = "url"
        article.is_biography.return_value = True
        article.is_american.return_value = False
        api_article = API_Article.from_article(article)
        assert api_article == API_Article("title", "url", True, False)


class Test_API_Nomination:
    def test_construction(self):
        api_article1 = API_Article("title1", "url1", True, True)
        api_article2 = API_Article("title2", "url2", False, False)
        api_hook1 = API_Hook("tag", "text")
        api_nomination = API_Nomination(
            "title", "url", True, [api_article1, api_article2], [api_hook1]
        )
        assert api_nomination.title == "title"
        assert api_nomination.url == "url"
        assert api_nomination.is_approved == True
        assert api_nomination.articles == [api_article1, api_article2]
        assert api_nomination.hooks == [api_hook1]

    def test_from_nomination(self, mocker):
        article1 = mocker.Mock(spec=dyk_tools.Article)
        article1.title.return_value = "title1"
        article1.url.return_value = "url1"
        article1.is_biography.return_value = True
        article1.is_american.return_value = True
        article2 = mocker.Mock(spec=dyk_tools.Article)
        article2.title.return_value = "title2"
        article2.url.return_value = "url2"
        article2.is_biography.return_value = False
        article2.is_american.return_value = False
        nomination = mocker.Mock(spec=dyk_tools.Nomination)
        nomination.title.return_value = "title"
        nomination.url.return_value = "url"
        nomination.is_approved.return_value = True
        nomination.articles.return_value = [article1, article2]
        nomination.hooks.return_value = [dyk_tools.Hook("tag", "text")]
        api_nomination = API_Nomination.from_nomination(nomination)
        assert api_nomination == API_Nomination(
            "title",
            "url",
            True,
            [
                API_Article("title1", "url1", True, True),
                API_Article("title2", "url2", False, False),
            ],
            [API_Hook("tag", "text")],
        )
