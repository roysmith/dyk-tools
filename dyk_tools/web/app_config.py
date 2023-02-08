from pathlib import Path

import toml

app_config = toml.load(Path.home() / "dyk-tools.toml")
