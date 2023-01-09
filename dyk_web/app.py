from flask import Flask, redirect, url_for, g

from pywikibot import Site

from . import core

app = Flask(__name__)
app.register_blueprint(core.bp)

@app.before_request
def set_site():
    g.site = Site("en", "wikipedia", "dyk-tools")


@app.route("/")
def home():
    return redirect(url_for("core.select"))
