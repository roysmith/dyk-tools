from contextlib import contextmanager

import pytest
from flask import template_rendered


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
