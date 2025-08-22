# app/cart/forms.py ?
from flask_wtf import FlaskForm
from wtforms import IntegerField, HiddenField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AddToCartForm(FlaskForm):
    product_id = HiddenField(validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    add = SubmitField("Add to Cart")
