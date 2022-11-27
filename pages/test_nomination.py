from pywikibot import Page
from nomination import Nomination

def test_nomination_can_be_constructed(self):
    page = Page()
    nomination = Nomination(page)
