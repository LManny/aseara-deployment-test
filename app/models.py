from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'supplier' or 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.email}, role={self.role}>"

    @property # What is this @property decorator?
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    admin_type = db.Column(db.String(20), nullable=False)  # 'absolute' or 'country'
    country_code = db.Column(db.String(5), nullable=True)  # e.g. 'MY', 'TH', 'PH', or null/None for admins

    user = db.relationship('User', backref=db.backref('admin', uselist=False))


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


# Supplier-related models
class SupplierStatus(enum.Enum):
    DRAFT = "draft"                # supplier hasn’t submitted yet
    SUBMITTED = "submitted"        # supplier clicked “Submit for review”
    UNDER_REVIEW = "under_review"  # admin opened/working
    NEEDS_MORE_INFO = "needs_more_info"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"        # optional: post-approval enforcement


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

    # File Uploads (Store keys -- which are basically paths)
    registration_cert_key = db.Column(db.String(255))  # Company cert
    bank_verification_doc_key = db.Column(db.String(255))  # Bank letter/statement
    director_id_doc_key = db.Column(db.String(255))  # NRIC/Passport

    # Metadata
    date_joined = db.Column(db.DateTime, default=db.func.current_timestamp())

    # What do I do about this code? Take form operational country?
    country_code = db.Column(db.String(2))  # used for country-admin scoping

    # Verification workflow
    status = db.Column(db.Enum(SupplierStatus), nullable=False, default=SupplierStatus.DRAFT)
    submitted_at = db.Column(db.DateTime)
    reviewed_at  = db.Column(db.DateTime)
    reviewed_by  = db.Column(db.Integer, db.ForeignKey('admin.id'))

    # Optional: short notes (admin → supplier)
    reviewer_note = db.Column(db.String(500))
    # Optional: supplier note when re-submitting
    submitter_note = db.Column(db.String(500))

    # Relationship
    user = db.relationship('User', backref=db.backref('supplier', uselist=False))
    reviewer = db.relationship('Admin', backref=db.backref('reviewed_suppliers', lazy=True))

    # Test if supplier can list products -- i.e. if Status = APPROVED
    @property
    def can_list_products(self) -> bool:
        return self.status == SupplierStatus.APPROVED

class SupplierDocument(db.Model):
    __tablename__ = "supplier_document"

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer,
                            db.ForeignKey("supplier.id", ondelete="CASCADE"),
                            nullable=False, index=True)

    # what the doc is
    kind = db.Column(db.String(50), nullable=False)  # e.g. "registration_cert", "bank_verification", "director_id"
    # where it’s stored (local key or S3 key)
    key = db.Column(db.String(512), nullable=False)  # e.g. "suppliers/42/documents/registration_cert/uuid.pdf"
    content_type = db.Column(db.String(100))
    size_bytes = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    supplier = db.relationship("Supplier", backref=db.backref(
        "documents", lazy="dynamic", cascade="all, delete-orphan", passive_deletes=True
    ))

    __table_args__ = (
        db.Index("ix_supplierdoc_supplier_kind", "supplier_id", "kind"),
        # If you want ONLY one of each kind per supplier, uncomment:
        # db.UniqueConstraint("supplier_id", "kind", name="uq_supplierdoc_per_kind"),
    )




# Product-related models
class ProductStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"   # optional, if you moderate listings
    LIVE = "live"
    PAUSED = "paused"
    ARCHIVED = "archived"

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=False)

    # Identity & SEO
    name = db.Column(db.String(200), nullable=False)
    short_desc = db.Column(db.String(300))       # one-line card blurb
    description = db.Column(db.Text)             # full detail
    slug = db.Column(db.String(220), unique=True)  # optional: for pretty URLs

    # Classification
    category = db.Column(db.String(120), index=True)     # normalize later
    subcategory = db.Column(db.String(120), index=True)
    hs_code = db.Column(db.String(20))                   # customs classification
    country_of_origin = db.Column(db.String(2), index=True)  # ISO-2 (e.g., "MY")

    # Commerce
    price = db.Column(db.Numeric(10, 2), nullable=False)    # store money in Decimal
    currency = db.Column(db.String(3), default="USD")    # "USD", "MYR", etc.
    moq = db.Column(db.Integer, default=1)               # minimum order qty
    stock = db.Column(db.Integer, default=0)             # simple stock control

    # Logistics (lightweight, can expand later)
    lead_time_days = db.Column(db.Integer)               # manufacturing/handling
    incoterms = db.Column(db.String(20))                 # "FOB", "CIF", "DDP", ...

    # Status & moderation
    status = db.Column(db.Enum(ProductStatus), nullable=False, default=ProductStatus.DRAFT)
    is_deleted = db.Column(db.Boolean, default=False)    # soft delete

    # Media (main image path; others go in ProductImage)
    main_image_path = db.Column(db.String(255))

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now())

    # Relationships
    supplier = db.relationship("Supplier", backref=db.backref("products", lazy="dynamic"))

class ProductImage(db.Model):
    __tablename__ = "product_image"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    path = db.Column(db.String(255), nullable=False)     # e.g. "uploads/products/xyz.jpg"
    alt_text = db.Column(db.String(200))
    sort_order = db.Column(db.Integer, default=0)

    product = db.relationship("Product", backref=db.backref(
        "images", cascade="all, delete-orphan", order_by="ProductImage.sort_order"
    ))

