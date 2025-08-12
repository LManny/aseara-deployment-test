from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'supplier'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.email}, role={self.role}>"

    @property # What is this @property decorator?
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    # Address
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postcode = db.Column(db.String(20))
    country = db.Column(db.String(100))

    # Contact
    phone_number = db.Column(db.String(20))

    # Metadata
    date_joined = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)

    # This has to be true first before the profile can be used
    profile_complete = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('customer', uselist=False))

    def __repr__(self):
        return f"<{self.address_line1}, {self.city}, {self.state}, {self.postcode}, {self.country}, {self.phone_number}>"


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    # Business Details
    business_name = db.Column(db.String(255))
    company_registration_number = db.Column(db.String(100), unique=True)
    nature_of_business = db.Column(db.String(255))
    tax_id_number = db.Column(db.String(100))  # TIN/SST/GST

    # Director Details
    director_name = db.Column(db.String(255))

    # Contact Person - Primary
    contact_name = db.Column(db.String(255))
    contact_designation = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))

    # Contact Person - Alternate (optional)
    alt_contact_name = db.Column(db.String(255))
    alt_contact_designation = db.Column(db.String(100))
    alt_contact_email = db.Column(db.String(120))
    alt_contact_phone = db.Column(db.String(20))

    # Address - Registered
    reg_address_line1 = db.Column(db.String(255))
    reg_address_line2 = db.Column(db.String(255))
    reg_city = db.Column(db.String(100))
    reg_state = db.Column(db.String(100))
    reg_postcode = db.Column(db.String(20))
    reg_country = db.Column(db.String(100))

    # Address - Operational
    op_address_line1 = db.Column(db.String(255))
    op_address_line2 = db.Column(db.String(255))
    op_city = db.Column(db.String(100))
    op_state = db.Column(db.String(100))
    op_postcode = db.Column(db.String(20))
    op_country = db.Column(db.String(100))

    # Bank Details
    bank_name = db.Column(db.String(100))
    bank_account_number = db.Column(db.String(50))

    # File Uploads (Store filenames or paths)
    registration_cert_path = db.Column(db.String(255))  # Company cert
    bank_verification_doc_path = db.Column(db.String(255))  # Bank letter/statement
    director_id_doc_path = db.Column(db.String(255))  # NRIC/Passport

    # Metadata
    is_verified = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=db.func.current_timestamp())

    # This has to be true first before the profile can be used
    profile_complete = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship('User', backref=db.backref('supplier', uselist=False))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)

    image_path = db.Column(db.String(255))  # store filename/path

    is_active = db.Column(db.Boolean, default=False)  # visible to customers

    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationship
    supplier = db.relationship('Supplier', backref=db.backref('products', lazy=True))