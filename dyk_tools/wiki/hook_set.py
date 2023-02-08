from dataclasses import dataclass
import re
from typing import Iterable

import mwparserfromhell as mwp
from pywikibot import Page


@dataclass(frozen=True)
class HookSet:
    page: Page

    def title(self) -> str:
        return self.page.title()

    def url(self) -> str:
        return self.page.full_url()

    def get_hooks(self) -> Iterable[str]:
        START_END = re.compile(
            r"""^(.*<!--\s*Hooks\s*-->)
            (.*)
            (<!--\s*HooksEnd\s*-->.*)$""",
            flags=re.S | re.X,
        )
        m = START_END.search(self.page.text)
        if not m:
            return []
        for line in m.group(2).splitlines():
            if line.startswith("* ..."):
                yield line.removeprefix("* ...")
