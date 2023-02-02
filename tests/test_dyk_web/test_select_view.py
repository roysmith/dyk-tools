from contextlib import contextmanager
from urllib.parse import unquote_plus

from flask import template_rendered
import pytest

from dyk_web.app import create_app
import dyk_web.core

# https://flask.palletsprojects.com/en/2.2.x/signals/
@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def get_pending_nominations(mocker):
    gpn = mocker.patch("dyk_web.core.get_pending_nominations", autospec=True)
    gpn.return_value = []
    print("--> gpn:", type(gpn))
    return gpn


def test_get(client, app, get_pending_nominations):
    with captured_templates(app) as templates:
        response = client.get("/select")
    assert response.status_code == 200
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == "select.html"
    assert "template_form" in context
    assert "prep_form" in context


def test_post_template_form_returns_redirect(client, app):
    response = client.post(
        "/select",
        follow_redirects=False,
        data={"submit-template": True, "name": "foo"},
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/display?template_name=foo"


def test_post_prep_form_returns_redirect(client, app):
    response = client.post(
        "/select",
        follow_redirects=False,
        data={"submit-prep": True, "name": "Template:Did you know/Preparation area 1"},
    )
    assert response.status_code == 302
    location = unquote_plus(response.headers["location"])
    assert location == "/prep?title=Template:Did you know/Preparation area 1"
