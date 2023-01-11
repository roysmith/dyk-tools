from dataclasses import asdict
import logging

from flask import Blueprint, request, g
from pywikibot import Page
from dyk_tools import Nomination
from .data import NominationData

bp = Blueprint("api", __name__, url_prefix="/api/v1")

logger = logging.getLogger("dyk_web.api")


@bp.route("/info")
def nomination_info():
    """template_name query arg is the DYK nomination template, including the Template: prefix."""
    page = Page(g.site, request.args["template_name"])
    nomination = Nomination(page)
    nomination_data = NominationData.from_nomination(nomination)
    return asdict(nomination_data)
