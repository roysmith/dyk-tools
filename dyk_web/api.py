from dataclasses import dataclass, asdict
import logging

from flask import Blueprint, request, g
from pywikibot import Page
from dyk_tools import Article, Nomination

bp = Blueprint("api", __name__, url_prefix="/api/v1")

logger = logging.getLogger("dyk_web.api")


@dataclass(frozen=True)
class API_Hook:
    tag: str
    text: str

    @staticmethod
    def from_hook(hook):
        """Construct an API_Hook from a dyk_tools.Hook"""
        return API_Hook(hook.tag, hook.text)


@dataclass(frozen=True)
class API_Article:
    title: str
    url: str
    is_biography: bool
    is_american: bool

    @staticmethod
    def from_article(article):
        """Construct an API_Article from a dyk_tools.Article"""
        return API_Article(
            article.title(), article.url(), article.is_biography(), article.is_american()
        )


@dataclass(frozen=True)
class API_Nomination:
    title: str
    url: str
    is_approved: bool
    articles: list[API_Article]
    hooks: list[API_Hook]

    @staticmethod
    def from_nomination(nomination):
        """Construct an API_Nomination from a dyk_tools.Nomination"""
        return API_Nomination(
            nomination.title(),
            nomination.url(),
            nomination.is_approved(),
            [API_Article.from_article(a) for a in nomination.articles()],
            [API_Hook.from_hook(h) for h in nomination.hooks()],
        )


@bp.route("/info")
def nomination_info():
    """template_name query arg is the DYK nomination template, including the Template: prefix."""
    page = Page(g.site, request.args["template_name"])
    nomination = Nomination(page)
    api_nomination = API_Nomination.from_nomination(nomination)
    print("a==> pi_nomination:", api_nomination)
    return asdict(api_nomination)
