try:
    import dyk_tools._version
except ModuleNotFoundError:
    version = "unknown"
    version_tuple = (0, 0, "", "")
else:
    version = dyk_tools._version.version
    version_tuple = dyk_tools._version.version_tuple
