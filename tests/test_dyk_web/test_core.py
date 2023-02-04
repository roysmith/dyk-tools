from urllib.parse import unquote_plus

import pytest


@pytest.fixture(autouse=True)
def get_pending_nominations(mocker):
    gpn = mocker.patch("dyk_web.core.get_pending_nominations", autospec=True)
    gpn.return_value = []
    return gpn


@pytest.fixture
def core_page(mocker, site):
    """Returns a mock pywikibot.Page."""
    mock_Page = mocker.patch("dyk_web.core.Page", autospec=True)
    return mock_Page(site)


class TestSelect:
    def test_get(self, client, app, captured_templates):
        with captured_templates(app) as templates:
            response = client.get("/select")
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "select.html"
        assert "nomination_form" in context
        assert "hook_set_form" in context

    def test_post_nomination_form_returns_redirect(self, client):
        response = client.post(
            "/select",
            follow_redirects=False,
            data={"submit-nomination": True, "name": "foo"},
        )
        assert response.status_code == 302
        assert response.headers["location"] == "/nomination?title=foo"

    def test_post_hook_set_form_returns_redirect(self, client):
        response = client.post(
            "/select",
            follow_redirects=False,
            data={
                "submit-hook-set": True,
                "name": "Template:Did you know/Preparation area 1",
            },
        )
        assert response.status_code == 302
        location = unquote_plus(response.headers["location"])
        assert location == "/hook-set?title=Template:Did you know/Preparation area 1"


class TestNomination:
    def test_get(self, client, app, captured_templates, core_page):
        core_page.get.return_value = ""
        with captured_templates(app) as templates:
            response = client.get("/nomination?title=foo")
        assert response.status_code == 200
        template, context = templates[0]
        assert template.name == "nomination.html"
        assert "nomination" in context


class TestHookSet:
    def test_get(self, client, app, captured_templates, core_page):
        core_page.text = ""
        with captured_templates(app) as templates:
            response = client.get("/hook-set?title=foo")
        assert response.status_code == 200
        template, context = templates[0]
        assert template.name == "hook-set.html"
        assert "data" in context
