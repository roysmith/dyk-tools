from contextlib import contextmanager

from flask import template_rendered
import pytest

from dyk_web.app import create_app

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


def test_get(client, app):
    with captured_templates(app) as templates:
        response = client.get("/select")
    assert response.status_code == 200
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == "select.html"


def test_post_template_form(client, app):
    response = client.post("")
