import os
from typing import Iterable

from flask import Blueprint, render_template, request, redirect, url_for, g, current_app
from pywikibot import Page, Category
from dyk_tools import Nomination, Article, HookSet
from .core_forms import NominationForm, HookSetForm
from .data import NominationData, HookSetData


bp = Blueprint("core", __name__)


@bp.route("/select", methods=["GET", "POST"])
def select():
    nf = NominationForm(request.form)
    hsf = HookSetForm(request.form)
    if request.method == "POST":
        if "submit-nomination" in request.form:
            return redirect(url_for("core.nomination", title=nf.name.data))
        if "submit-hook-set" in request.form:
            return redirect(url_for("core.hook_set", title=hsf.name.data))
    nf.name.choices = pending_nominations()
    hsf.name.choices = hook_set_choices(g.site)
    return render_template("select.html", nomination_form=nf, hook_set_form=hsf)


@bp.route("/nomination")
def nomination():
    """title query arg is the DYK nomination template, including the Template: prefix."""
    current_app.logger.info("Running on %s", os.uname().nodename)
    page = Page(g.site, request.args["title"])
    nomination = Nomination(page)
    nomination_data = NominationData.from_nomination(nomination)
    return render_template("nomination.html", nomination=nomination_data)


@bp.route("/hook-set")
def hook_set():
    page = Page(g.site, request.args["title"])
    hook_set = HookSet(page)
    hook_set_data = HookSetData.from_hook_set(hook_set, page.site)
    return render_template("hook-set.html", data=hook_set_data)


def pending_nominations():
    cat = Category(g.site, "Pending DYK nominations")
    titles = []
    for nom in cat.articles():
        title = nom.title()
        titles.append((title, title.removeprefix("Template:Did you know nominations/")))
    return titles


def hook_set_choices(site) -> list[(str, str)]:
    choices = []
    for i in queue_sequence(site):
        choices.append((f"Template:Did you know/Queue/{i}", f"Queue {i}"))
    for i in prep_sequence(site):
        choices.append(
            (f"Template:Did you know/Preparation area {i}", f"Prep area {i}")
        )
    return choices


def queue_sequence(site) -> Iterable[int]:
    page = Page(site, "Template:Did you know/Queue/Next")
    start = int(page.extract())
    return hook_set_sequence(start)


def prep_sequence(site) -> Iterable[int]:
    page = Page(site, "Template:Did you know/Queue/NextPrep")
    start = int(page.extract())
    return hook_set_sequence(start)


def hook_set_sequence(i) -> Iterable[int]:
    """Returns a list of 7 integers starting at i and wrapping around
    from 7 to 1 (not 0), like the hook sets are numbered.

    """
    for count in range(7):
        yield i
        i = (i + 1) if i < 7 else 1
