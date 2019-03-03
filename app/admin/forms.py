from wtforms import Form, PasswordField, validators


class PasswordResetAdminForm(Form):
    password = PasswordField('Password', [validators.data_required()])
