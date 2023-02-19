"""This collection of classes are intended to be fully static immutable
data structures, in the style of Google protobufs.  They are serializable,
hashable, and thread-safe.

Python, of course, doesn't have truly immutable data.  If you try hard
enough, you can get around the frozen-ness of these classes.  So don't
do that.

"""

from dataclasses import dataclass

from .cache import cache


@dataclass(frozen=True)
class HookData:
    text: str
    tag: str

    @staticmethod
    def from_hook(hook):
        """Construct a HookData from a dyk_tools.Hook"""
        return HookData(hook.text, hook.tag)


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
    @cache.memoize(timeout=600)
    def from_nomination(nomination):
        """Construct a NominationData from a dyk_tools.Nomination"""
        return NominationData(
            nomination.title(),
            nomination.url(),
            nomination.is_approved(),
            [ArticleData.from_article(a) for a in nomination.articles()],
            [HookData.from_hook(h) for h in nomination.hooks()],
        )


@dataclass(frozen=True)
class HookSetData:
    title: str
    url: str
    hooks: list[str]
    rendered_hooks: list[str]

    @staticmethod
    @cache.memoize(timeout=600)
    def from_hook_set(hook_set, site):
        """Construct a HookSetData from a dyk_tools.HookSet"""
        hooks = list(hook_set.get_hooks())
        rendered_hooks = [h.render(site) for h in hooks]
        return HookSetData(hook_set.title(), hook_set.url(), hooks, rendered_hooks)
