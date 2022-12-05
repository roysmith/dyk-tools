from flask import Flask, render_template, request, redirect, url_for
from pywikibot import Site, Page

from template_form import TemplateForm
from dyk_tools.nomination import Nomination

app = Flask(__name__)

SITE = Site('en', 'wikipedia')

@app.route("/", methods=["GET", "POST"])
def home_page():
    form = TemplateForm(request.form)
    if request.method == "POST" and form.validate():
        return redirect(url_for("display", template_name=form.name.data))
    return render_template("home_page.html", form=form)


@app.route("/display/<template_name>")
def display(template_name):
    """template_name is the DYK nomination template, without the Template: prefix."""
    page = Page (SITE, f'Template:{template_name}')
    nomination = Nomination(page)

    return render_template("display.html", title=nomination.page.title(), approved=nomination.is_approved())
