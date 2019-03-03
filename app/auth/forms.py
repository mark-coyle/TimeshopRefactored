from wtforms import Form, StringField, PasswordField, validators


class LoginForm(Form):
    username = StringField('Username', [validators.length(min=4, max=20)])
    password = PasswordField('Password',
                             [
                                 validators.data_required(),
                             ])


class RegisterForm(Form):
    first_name = StringField('First Name', [validators.length(min=1, max=50)])
    last_name = StringField('Last Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=20)])
    email = StringField('Email', [validators.data_required()])
    password = PasswordField('Password',
                             [
                                 validators.data_required(),
                                 validators.EqualTo(
                                     'confirm', message='Passwords do not match')
                             ])
    confirm = PasswordField('Confirm Password')


class PasswordChangeForm(Form):
    current_password = PasswordField(
        'Current Password', [validators.data_required()])
    new_password = PasswordField('New Password',
                                 [
                                     validators.data_required(),
                                     validators.EqualTo(
                                         'confirm', message='Passwords do not match')
                                 ])
    confirm = PasswordField('Confirm Password')