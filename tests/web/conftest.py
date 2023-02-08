from contextlib import contextmanager

import pytest
from flask import template_rendered

from dyk_tools.web.app import create_app


# Based on example in https://flask.palletsprojects.com/en/2.2.x/signals/
@pytest.fixture
def captured_templates():
    @contextmanager
    def _captured_templates(app):
        recorded = []

        def record(sender, template, context, **extra):
            recorded.append((template, context))

        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

    return _captured_templates


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
