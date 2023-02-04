from urllib.parse import unquote_plus

import pytest

from dyk_web.core import queue_sequence, prep_sequence, hook_set_choices


@pytest.fixture  # (autouse=True)
def mock_pending_nominations(mocker):
    return mocker.patch("dyk_web.core.pending_nominations", autospec=True)


@pytest.fixture
def mock_hook_set_choices(mocker):
    return mocker.patch("dyk_web.core.hook_set_choices", autospec=True)


@pytest.fixture
def core_page(mocker, site):
    """Returns a mock pywikibot.Page."""
    mock_Page = mocker.patch("dyk_web.core.Page", autospec=True)
    return mock_Page(site)


class TestSelect:
    def test_get(
        self,
        client,
        app,
        captured_templates,
        mock_pending_nominations,
        mock_hook_set_choices,
    ):
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


class TestPrepSequence:
    def test_returns_int(self, site, core_page):
        core_page.extract.return_value = "3"
        assert list(prep_sequence(site)) == [3, 4, 5, 6, 7, 1, 2]


class TestQueueSequence:
    def test_returns_int(self, site, core_page):
        core_page.extract.return_value = "5"
        assert list(queue_sequence(site)) == [5, 6, 7, 1, 2, 3, 4]


class TestHookSetChoices:
    def test_returns_correct_page_names(self, mocker, site):
        queue_sequence = mocker.patch("dyk_web.core.queue_sequence", autospec=True)
        prep_sequence = mocker.patch("dyk_web.core.prep_sequence", autospec=True)
        queue_sequence.return_value = [3, 4, 5, 6, 7, 1, 2]
        prep_sequence.return_value = [5, 6, 7, 1, 2, 3, 4]

        choices = hook_set_choices(site)
        assert choices == [
            ("Template:Did you know/Queue/3", "Queue 3"),
            ("Template:Did you know/Queue/4", "Queue 4"),
            ("Template:Did you know/Queue/5", "Queue 5"),
            ("Template:Did you know/Queue/6", "Queue 6"),
            ("Template:Did you know/Queue/7", "Queue 7"),
            ("Template:Did you know/Queue/1", "Queue 1"),
            ("Template:Did you know/Queue/2", "Queue 2"),
            ("Template:Did you know/Preparation area 5", f"Prep area 5"),
            ("Template:Did you know/Preparation area 6", f"Prep area 6"),
            ("Template:Did you know/Preparation area 7", f"Prep area 7"),
            ("Template:Did you know/Preparation area 1", f"Prep area 1"),
            ("Template:Did you know/Preparation area 2", f"Prep area 2"),
            ("Template:Did you know/Preparation area 3", f"Prep area 3"),
            ("Template:Did you know/Preparation area 4", f"Prep area 4"),
        ]
