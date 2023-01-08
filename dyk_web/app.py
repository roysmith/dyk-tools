from flask import Flask, redirect, url_for

from . import core

app = Flask(__name__)
app.register_blueprint(core.bp)


@app.route("/")
def home():
    return redirect(url_for("core.select"))
