from wtforms import Form, SelectField


class TemplateForm(Form):
    # See https://github.com/wtforms/wtforms/issues/762
    name = SelectField(validate_choice=False, choices=[])
