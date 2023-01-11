from flask_caching import Cache

config = {"CACHE_TYPE": "SimpleCache"}

cache = Cache(config=config)
