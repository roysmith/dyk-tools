from wtforms import Form, SelectField, SubmitField, RadioField


class NominationForm(Form):
    # See https://github.com/wtforms/wtforms/issues/762
    name = SelectField(validate_choice=False, choices=[])
    submit = SubmitField(name="submit-nomination", label="Submit")


class HookSetForm(Form):
    name = RadioField(validate_choice=False, choices=[])
    submit = SubmitField(name="submit-hook-set", label="Submit")
