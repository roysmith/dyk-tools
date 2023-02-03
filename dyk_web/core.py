import os

from flask import Blueprint, render_template, request, redirect, url_for, g, current_app
from pywikibot import Page, Category
from dyk_tools import Nomination, Article, HookSet
from dyk_web.core_forms import TemplateForm, HookSetForm
from dyk_web.data import NominationData, HookSetData


bp = Blueprint("core", __name__)


@bp.route("/select", methods=["GET", "POST"])
def select():
    tf = TemplateForm(request.form)
    pf = HookSetForm(request.form)
    if request.method == "POST":
        if "submit-template" in request.form and tf.validate():
            return redirect(url_for("core.display", template_name=tf.name.data))
        if "submit-hook-set" in request.form and pf.validate():
            return redirect(url_for("core.hook_set", title=pf.name.data))
    tf.name.choices = get_pending_nominations()
    return render_template("select.html", template_form=tf, hook_set_form=pf)


def get_pending_nominations():
    cat = Category(g.site, "Pending DYK nominations")
    titles = []
    for nom in cat.articles():
        title = nom.title()
        titles.append((title, title.removeprefix("Template:Did you know nominations/")))
    return titles


@bp.route("/display")
def display():
    """template_name query arg is the DYK nomination template, including the Template: prefix."""
    current_app.logger.info("Running on %s", os.uname().nodename)
    page = Page(g.site, request.args["template_name"])
    nomination = Nomination(page)
    nomination_data = NominationData.from_nomination(nomination)
    return render_template("display.html", nomination=nomination_data)


@bp.route("/hook-set")
def hook_set():
    page = Page(g.site, request.args["title"])
    hook_set = HookSet(page)
    hook_set_data = HookSetData.from_hook_set(hook_set)
    return render_template("hook-set.html", data=hook_set_data)
