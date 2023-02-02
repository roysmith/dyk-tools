from wtforms import Form, SelectField, SubmitField, RadioField


class TemplateForm(Form):
    # See https://github.com/wtforms/wtforms/issues/762
    name = SelectField(validate_choice=False, choices=[])
    submit = SubmitField(name="submit-template", label="Submit")


class PrepForm(Form):
    name = RadioField(
        choices=[
            (f"Template:Did you know/Preparation area {i}", i)
            for i in [1, 2, 3, 4, 5, 6, 7]
        ]
    )
    submit = SubmitField(name="submit-prep", label="Submit")
