from wtforms import Form, SelectField, SubmitField, RadioField


class NominationForm(Form):
    # See https://github.com/wtforms/wtforms/issues/762
    name = SelectField(validate_choice=False, choices=[])
    submit = SubmitField(name="submit-nomination", label="Submit")


class HookSetForm(Form):
    name = RadioField(
        choices=[
            (f"Template:Did you know/Preparation area {i}", f"Prep {i}")
            for i in [1, 2, 3, 4, 5, 6, 7]
        ]
        + [
            (f"Template:Did you know/Queue/{i}", f"Queue {i}")
            for i in [1, 2, 3, 4, 5, 6, 7]
        ]
    )
    submit = SubmitField(name="submit-hook-set", label="Submit")
