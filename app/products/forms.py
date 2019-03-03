from wtforms import Form, StringField, SelectField, TextAreaField, IntegerField, FileField, validators


class AddProductForm(Form):
    name = StringField('Product Name', [validators.length(min=1, max=50)])
    product_type = SelectField('Product Type', coerce=int, choices=[(
        1, "Pocket Watches"), (2, "Modern Watches"), (3, "Classic Watches"), (4, "Smart Watches")], default=1,)
    description = StringField('Product Description', [
                              validators.length(min=4, max=300)])
    price = IntegerField('Product Price', [validators.data_required()])
    quantity = IntegerField('Product Quantity', [validators.data_required()])
    image = FileField('Product Image')


class EditProductForm(Form):
    name = StringField('Product Name', [validators.length(min=1, max=50)])
    product_type = SelectField('Product Type', coerce=int, choices=[(
        1, "Pocket Watches"), (2, "Modern Watches"), (3, "Classic Watches"), (4, "Smart Watches")], default=1,)
    description = StringField('Product Description', [
                              validators.length(min=4, max=300)])
    price = IntegerField('Product Price', [validators.data_required()])
    quantity = IntegerField('Product Quantity')
    image = FileField('Product Image')


class ReviewForm(Form):
    title = StringField('Title', [validators.length(min=1, max=100)])
    description = TextAreaField(
        'Review Content', [validators.length(min=1, max=1000)])
