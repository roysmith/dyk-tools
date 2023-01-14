import logging.config
import os
from pathlib import Path

from flask import Flask, redirect, url_for, g
from pywikibot import Site

from . import core, api
from .cache import cache, cache_config
from .app_config import app_config


# fmt: off
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(process)s/%(thread)d %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": Path.home() / "dyk-tools-web.log",
                "formatter": "default",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": [app_config["logging"]["handler"]]},
    }
)
# fmt: on

app = Flask(__name__)
app.register_blueprint(core.bp)
app.register_blueprint(api.bp)
cache.init_app(app)

app.logger.info(f"Running on {os.uname().nodename}")
app.logger.info(f"Using {cache_config['CACHE_TYPE']}")


@app.before_request
def set_site():
    g.site = Site("en", "wikipedia", "dyk-tools")


@app.route("/")
def home():
    return redirect(url_for("core.select"))
