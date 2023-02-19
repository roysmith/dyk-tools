from textwrap import dedent

from dyk_tools import Hook, Article, Nomination
from dyk_tools.web.data import HookData, ArticleData, NominationData


class Test_HookData:
    def test_construction(self):
        hook_data = HookData("text", "tag")
        assert hook_data.text == "text"
        assert hook_data.tag == "tag"

    def test_from_hook(self, site):
        hook = Hook("text", "tag")
        hook_data = HookData.from_hook(hook)
        assert hook_data.text == "text"
        assert hook_data.tag == "tag"


class Test_ArticleData:
    def test_construction(self):
        article_data = ArticleData("Title", "url", True, False)
        assert article_data.title == "Title"
        assert article_data.url == "url"
        assert article_data.is_biography == True
        assert article_data.is_american == False

    def test_from_article(self, mocker):
        article = mocker.Mock(spec=Article)
        article.title.return_value = "title"
        article.url.return_value = "url"
        article.is_biography.return_value = True
        article.is_american.return_value = False
        article_data = ArticleData.from_article(article)
        assert article_data == ArticleData("title", "url", True, False)


class Test_NominationData:
    def test_construction(self):
        article_data1 = ArticleData("title1", "url1", True, True)
        article_data2 = ArticleData("title2", "url2", False, False)
        hook_data1 = HookData("text", "tag")
        nomination_data = NominationData(
            "title", "url", True, [article_data1, article_data2], [hook_data1]
        )
        assert nomination_data.title == "title"
        assert nomination_data.url == "url"
        assert nomination_data.is_approved == True
        assert nomination_data.articles == [article_data1, article_data2]
        assert nomination_data.hooks == [hook_data1]

    def test_from_nomination(self, mocker, site):
        article1 = mocker.Mock(spec=Article)
        article1.title.return_value = "title1"
        article1.url.return_value = "url1"
        article1.is_biography.return_value = True
        article1.is_american.return_value = True
        article2 = mocker.Mock(spec=Article)
        article2.title.return_value = "title2"
        article2.url.return_value = "url2"
        article2.is_biography.return_value = False
        article2.is_american.return_value = False
        nomination = mocker.Mock(spec=Nomination)
        nomination.title.return_value = "title"
        nomination.url.return_value = "url"
        nomination.is_approved.return_value = True
        nomination.articles.return_value = [article1, article2]
        nomination.hooks.return_value = [Hook("text", "tag")]
        nomination_data = NominationData.from_nomination.uncached(nomination)
        assert nomination_data == NominationData(
            "title",
            "url",
            True,
            [
                ArticleData("title1", "url1", True, True),
                ArticleData("title2", "url2", False, False),
            ],
            [HookData("text", "tag")],
        )
