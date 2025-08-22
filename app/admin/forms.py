# app/admin/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional

STATUS_CHOICES = [
    ("", "Submitted & Under Review"),
    ("submitted", "Submitted"),
    ("under_review", "Under Review"),
    ("needs_more_info", "Needs More Info"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

class VerificationFilterForm(FlaskForm):
    class Meta:
        csrf = False  # safe for GET-only forms; keeps URLs shareable

    q = StringField("Search", validators=[Optional()])
    status = SelectField("Status", choices=STATUS_CHOICES, validators=[Optional()])
    country = SelectField("Country", choices=[], validators=[Optional()])  # we’ll fill choices in the route
    submit = SubmitField("Apply")


class VerificationActionForm(FlaskForm):
    approve = SubmitField("Approve")
    needs_more_info = SubmitField("Needs Info")
    reject = SubmitField("Reject")

