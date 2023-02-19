from dataclasses import dataclass
import re
from typing import Iterable

import mwparserfromhell as mwp
from pywikibot import Page

from .hook import Hook


@dataclass(frozen=True)
class HookSet:
    page: Page

    def title(self) -> str:
        return self.page.title()

    def url(self) -> str:
        return self.page.full_url()

    def hooks(self) -> Iterable[Hook]:
        START_END = re.compile(
            r"""^(.*<!--\s*Hooks\s*-->)
            (.*)
            (<!--\s*HooksEnd\s*-->.*)$""",
            flags=re.DOTALL | re.VERBOSE,
        )
        m = START_END.search(self.page.text)
        if not m:
            return []
        for line in m.group(2).splitlines():
            if line.startswith("* ..."):
                wikitext = line.removeprefix("* ...")
                yield Hook(wikitext)

    def targets(self) -> Iterable[str]:
        for hook in self.hooks():
            for target in hook.targets():
                yield target
