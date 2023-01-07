try:
    import dyk_tools._version
except ModuleNotFoundError:
    version_string = "unknown"
    version_tuple = (0, 0, "", "")
else:
    version_string = dyk_tools._version.version
    version_tuple = dyk_tools._version.version_tuple
