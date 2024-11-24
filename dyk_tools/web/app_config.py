import os
from pathlib import Path

import toml

base_dir = os.environ["DYK_TOOLS_BASEDIR"]
app_config = toml.load(Path(base_dir) / "dyk-tools.toml")
