"""This collection of classes are intended to be fully static data structures,
in the style of Google protobufs.  They can be serialized as JSON, hashed, or
stored in an external cache such as memcache or redis.

"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HookData:
    tag: str
    text: str

    @staticmethod
    def from_hook(hook):
        """Construct an HookData from a dyk_tools.Hook"""
        return HookData(hook.tag, hook.text)


@dataclass(frozen=True)
class ArticleData:
    title: str
    url: str
    is_biography: bool
    is_american: bool

    @staticmethod
    def from_article(article):
        """Construct an ArticleData from a dyk_tools.Article"""
        return ArticleData(
            article.title(),
            article.url(),
            article.is_biography(),
            article.is_american(),
        )


@dataclass(frozen=True)
class NominationData:
    title: str
    url: str
    is_approved: bool
    articles: list[ArticleData]
    hooks: list[HookData]

    @staticmethod
    def from_nomination(nomination):
        """Construct an NominationData from a dyk_tools.Nomination"""
        return NominationData(
            nomination.title(),
            nomination.url(),
            nomination.is_approved(),
            [ArticleData.from_article(a) for a in nomination.articles()],
            [HookData.from_hook(h) for h in nomination.hooks()],
        )
