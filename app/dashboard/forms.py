from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, FileField, DecimalField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length, Email, NumberRange

from decimal import Decimal


class CustomerProfileForm(FlaskForm):

    # # Should I remove the first_name and last_name fields as this was already added in? They shouldn't have the option to change this right?
    # first_name = StringField("First Name", validators=[DataRequired(), Length(max=100)])
    # last_name = StringField("Last Name", validators=[DataRequired(), Length(max=100)])

    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(max=20)])

    address_line1 = StringField("Address Line 1", validators=[DataRequired(), Length(max=255)])
    address_line2 = StringField("Address Line 2", validators=[DataRequired(), Length(max=255)])
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    state = StringField("State", validators=[DataRequired(), Length(max=100)])
    postcode = StringField("Postcode", validators=[DataRequired(), Length(max=20)])
    country = SelectField(coerce=str, validators=[DataRequired()])

    submit = SubmitField("Save Changes")


class SupplierVerificationForm(FlaskForm):
    # Business Details
    business_name = StringField('Business Name', validators=[DataRequired()])
    company_registration_number = StringField('Company Registration Number', validators=[DataRequired()])
    nature_of_business = StringField('Nature of Business', validators=[DataRequired()])
    tax_id_number = StringField('Tax ID Number', validators=[DataRequired()])

    # Director
    director_name = StringField('Director Name', validators=[DataRequired()])

    # Contact Person - Primary
    contact_name = StringField('Primary Contact Name', validators=[DataRequired()])
    contact_designation = StringField('Designation', validators=[DataRequired()])
    contact_email = StringField('Email', validators=[DataRequired(), Email()])
    contact_phone = StringField('Phone', validators=[DataRequired()])

    # Contact Person - Alternate (Optional)
    alt_contact_name = StringField('Alt. Contact Name', validators=[Optional()])
    alt_contact_designation = StringField('Alt. Designation', validators=[Optional()])
    alt_contact_email = StringField('Alt. Email', validators=[Optional(), Email()])
    alt_contact_phone = StringField('Alt. Phone', validators=[Optional()])

    # Registered Address
    reg_address_line1 = StringField('Reg. Address Line 1', validators=[DataRequired()])
    reg_address_line2 = StringField('Reg. Address Line 2', validators=[Optional()])
    reg_city = StringField('City', validators=[DataRequired()])
    reg_state = StringField('State', validators=[DataRequired()])
    reg_postcode = StringField('Postcode', validators=[DataRequired()])
    reg_country = SelectField(coerce=str, validators=[DataRequired()])

    # Operational Address
    op_address_line1 = StringField('Op. Address Line 1', validators=[DataRequired()])
    op_address_line2 = StringField('Op. Address Line 2', validators=[Optional()])
    op_city = StringField('City', validators=[DataRequired()])
    op_state = StringField('State', validators=[DataRequired()])
    op_postcode = StringField('Postcode', validators=[DataRequired()])
    op_country = SelectField(coerce=str, validators=[DataRequired()])

    # Bank
    bank_name = StringField('Bank Name', validators=[DataRequired()])
    bank_account_number = StringField('Bank Account Number', validators=[DataRequired()])

    # Documents
    registration_cert = FileField('Registration Certificate', validators=[Optional()])
    bank_verification_doc = FileField('Bank Verification Document', validators=[Optional()])
    director_id_doc = FileField('Director ID Document', validators=[Optional()])

    submit = SubmitField('Submit Verification')



COMMON_CURRENCIES = [("USD","USD"), ("MYR","MYR"), ("SGD","SGD"), ("THB","THB"), ("IDR","IDR"), ("VND","VND"), ("PHP","PHP")]
INCOTERMS = [("", "—"), ("EXW","EXW"), ("FOB","FOB"), ("CIF","CIF"), ("DDP","DDP")]

class AddProductForm(FlaskForm):
    # Identity
    name = StringField("Product Name", validators=[DataRequired(), Length(max=200)])
    short_desc = StringField("Short Description", validators=[Optional(), Length(max=300)])
    description = TextAreaField("Full Description", validators=[Optional()])

    # Classification
    category = StringField("Category", validators=[Optional(), Length(max=120)])
    subcategory = StringField("Subcategory", validators=[Optional(), Length(max=120)])
    hs_code = StringField("HS Code", validators=[Optional(), Length(max=20)])
    country_of_origin = StringField("Country of Origin (ISO-2)", validators=[Optional(), Length(max=2)])

    # Commerce
    price = DecimalField("Price", places=2, rounding=None, validators=[DataRequired(message="Enter a price")], default=Decimal("0.00"))
    currency = SelectField("Currency", choices=COMMON_CURRENCIES, default="USD")
    moq = IntegerField("Minimum Order Quantity (MOQ)", validators=[Optional(), NumberRange(min=1)], default=1)
    stock = IntegerField("Stock", validators=[Optional(), NumberRange(min=0)], default=0)

    # Logistics
    lead_time_days = IntegerField("Lead Time (days)", validators=[Optional(), NumberRange(min=0)])
    incoterms = SelectField("Incoterms", choices=INCOTERMS, default="")

    # # One main image
    # main_image = FileField(
    #     "Main Image",
    #     validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only (jpg, png, webp).")]
    # )

    # Actions
    save_draft = SubmitField("Save as Draft")
    publish = SubmitField("Publish")
