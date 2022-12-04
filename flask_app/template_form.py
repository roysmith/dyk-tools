from wtforms import Form, StringField

class TemplateForm(Form):
    name = StringField('Name')
