import os
from pathlib import Path

import toml

base_dir = Path(os.environ["DYK_TOOLS_BASEDIR"])
app_config = toml.load(base_dir / "dyk-tools.toml")
