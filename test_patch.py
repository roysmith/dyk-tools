from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from pywikibot import Site, Page

class PatchTest(TestCase):
    def test_patch(self):
        with patch('pywikibot.Site') as mock_site:
            with patch('pywikibot.Page') as mock_page:
                site = mock_site('xx', 'wikipedia')
                page = mock_page(site, 'User:RoySmith')
                print(page.get())
