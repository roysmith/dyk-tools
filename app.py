from flask import Flask, render_template, request, redirect, url_for
from pywikibot import Site, Page, Category
from template_form import TemplateForm
from dyk_tools import Nomination

app = Flask(__name__)

SITE = Site("en", "wikipedia", "dyk-tools")


@app.route("/", methods=["GET", "POST"])
def home_page():
    form = TemplateForm(request.form)
    if request.method == "POST" and form.validate():
        return redirect(url_for("display", template_name=form.name.data))
    form.name.choices = get_pending_nominations()
    return render_template("home_page.html", form=form)


def get_pending_nominations():
    cat = Category(SITE, "Pending DYK nominations")
    titles = []
    for nom in cat.articles():
        title = nom.title()
        titles.append((title, title.removeprefix("Template:Did you know nominations/")))
    return titles


@app.route("/display")
def display():
    """template_name query arg is the DYK nomination template, including the Template: prefix."""
    page = Page(SITE, request.args["template_name"])
    return render_template("display.html", nomination=Nomination(page))
