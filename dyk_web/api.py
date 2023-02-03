from dataclasses import asdict

from flask import Blueprint, request, g, current_app
from pywikibot import Page
from dyk_tools import Nomination
from .data import NominationData


bp = Blueprint("api", __name__, url_prefix="/api/v1")


@bp.route("/nomination")
def nomination():
    """title query arg is the DYK nomination template, including the Template: prefix."""
    current_app.logger.info("logger is %s", current_app.logger)
    page = Page(g.site, request.args["title"])
    nomination = Nomination(page)
    nomination_data = NominationData.from_nomination(nomination)
    return asdict(nomination_data)
