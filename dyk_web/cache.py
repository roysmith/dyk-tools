import os

from flask_caching import Cache

from dyk_tools.version import version_string


# Note: CACHE_KEY_PREFIX deliberately includes version_string
# so all cache entries are invalidated on any version change.
if "REDIS_CACHE_URL" in os.environ:
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_KEY_PREFIX": f"dyk-tools-{version_string}",
        "CACHE_REDIS_URL": os.environ["REDIS_CACHE_URL"],
    }
else:
    cache_config = {"CACHE_TYPE": "SimpleCache"}

cache = Cache(config=cache_config)
