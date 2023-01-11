from flask import Blueprint, render_template, request, redirect, url_for, g
from pywikibot import Page, Category
from dyk_tools import Nomination, Article
from dyk_web.template_form import TemplateForm
from dyk_web.data import NominationData

bp = Blueprint("core", __name__)


@bp.route("/select", methods=["GET", "POST"])
def select():
    form = TemplateForm(request.form)
    if request.method == "POST" and form.validate():
        return redirect(url_for("core.display", template_name=form.name.data))
    form.name.choices = get_pending_nominations()
    return render_template("select.html", form=form)


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
    page = Page(g.site, request.args["template_name"])
    nomination = Nomination(page)
    nomination_data = NominationData.from_nomination(nomination)
    return render_template("display.html", nomination=nomination_data)
