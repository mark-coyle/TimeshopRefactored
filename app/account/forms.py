from wtforms import Form, StringField, TextAreaField, PasswordField, validators


class EditAccountForm(Form):
    first_name = StringField('First Name', [validators.length(min=1, max=50)])
    last_name = StringField('Last Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=20)])
    email = StringField('Email', [validators.data_required()])
    shipping_address = TextAreaField(
        'Shipping Address', [validators.input_required()])


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
