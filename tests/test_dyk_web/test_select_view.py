from urllib.parse import unquote_plus

import pytest


@pytest.fixture(autouse=True)
def get_pending_nominations(mocker):
    gpn = mocker.patch("dyk_web.core.get_pending_nominations", autospec=True)
    gpn.return_value = []
    return gpn


def test_get(client, app, captured_templates):
    with captured_templates(app) as templates:
        response = client.get("/select")
    assert response.status_code == 200
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == "select.html"
    assert "nomination_form" in context
    assert "hook_set_form" in context


def test_post_nomination_form_returns_redirect(client, app):
    response = client.post(
        "/select",
        follow_redirects=False,
        data={"submit-nomination": True, "name": "foo"},
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/nomination?title=foo"


def test_post_hook_set_form_returns_redirect(client, app):
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
