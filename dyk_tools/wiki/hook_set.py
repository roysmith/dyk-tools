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

    @staticmethod
    def queue_sequence(site) -> Iterable[int]:
        page = Page(site, "Template:Did you know/Queue/Next")
        start = int(page.extract())
        return HookSet.hook_set_sequence(start)

    @staticmethod
    def prep_sequence(site) -> Iterable[int]:
        page = Page(site, "Template:Did you know/Queue/NextPrep")
        start = int(page.extract())
        return HookSet.hook_set_sequence(start)

    @staticmethod
    def hook_set_sequence(i) -> Iterable[int]:
        """Iterates over 7 integers starting at i and wrapping around
        from 7 to 1 (not 0), like the hook sets are numbered.

        """
        for count in range(7):
            yield i
            i = (i + 1) if i < 7 else 1
