from dyk_tools.wiki.nomination import Nomination
from dyk_tools.wiki.hook import Hook
from dyk_tools.wiki.article import Article
from dyk_tools.wiki.hook_set import HookSet

try:
    import dyk_tools._version
except ModuleNotFoundError:
    version = "unknown"
    version_tuple = (0, 0, "", "")
else:
    version = dyk_tools._version.version
    version_tuple = dyk_tools._version.version_tuple

__all__ = [
    "Article",
    "Hook",
    "Nomination",
    "HookSet",
    "version",
    "version_tuple",
]
