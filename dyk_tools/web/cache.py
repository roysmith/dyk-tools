from flask_caching import Cache

from dyk_tools.version import version_string
from .app_config import app_config


if "cache" in app_config:
    cache_config = app_config["cache"]
    cache_config["CACHE_KEY_PREFIX"] = f"dyk-tools.{version_string}.web"
else:
    cache_config = {"CACHE_TYPE": "NullCache"}

cache = Cache(config=cache_config)
