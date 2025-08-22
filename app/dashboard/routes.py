from flask import render_template, redirect, url_for, abort, flash, request
from flask_login import login_required, current_user
from . import dashboard
from .forms import CustomerProfileForm, SupplierVerificationForm, AddProductForm
from app.models import Customer, Supplier, Product, SupplierStatus, SupplierDocument
from app.extensions import db

from storage_keys import supplier_doc_key
from storage_local import key_to_local_path, save_local

from pycountry import countries
from flask import current_app
from werkzeug.utils import secure_filename
import os

def upsert_supplier_doc(supplier_id: int, kind: str, file_storage, *, delete_old_local=False):
    """Create or replace a SupplierDocument for this supplier+kind."""
    if not (file_storage and file_storage.filename):
        return None

    # 1) generate a storage key and save bytes (dev: local; prod: S3 done client-side)
    key = supplier_doc_key(supplier_id, kind, file_storage.filename)
    save_local(file_storage, key)  # in prod you'd skip this because browser uploaded to S3

    # 2) upsert the DB row
    doc = SupplierDocument.query.filter_by(supplier_id=supplier_id, kind=kind).first()
    old_key = doc.key if doc else None

    if doc is None:
        doc = SupplierDocument(
            supplier_id=supplier_id,
            kind=kind,
            key=key,
            content_type=file_storage.mimetype,
            size_bytes=getattr(file_storage, "content_length", None),
        )
        db.session.add(doc)
    else:
        doc.key = key
        doc.content_type = file_storage.mimetype
        doc.size_bytes = getattr(file_storage, "content_length", None)

    # 3) optional: delete old local file to avoid orphans (dev only)
    if delete_old_local and old_key and old_key != key:
        try:
            key_to_local_path(old_key).unlink(missing_ok=True)
        except Exception:
            pass

    return doc


@dashboard.route('/')
@login_required
def user_dashboard():
    if current_user.role == 'customer':
        return redirect(url_for('dashboard.customer_dashboard'))
    elif current_user.role == 'supplier':
        return redirect(url_for('dashboard.supplier_dashboard'))
    return redirect(url_for('main.index'))

# Maybe add a redirect to the Admin dashboard too if the user is an admin? Or that doesn't really matter?


@dashboard.route('/customer')
@login_required # Does login redirect to the login page if user not logged in?
def customer_dashboard():
    if current_user.role != 'customer':
        abort(403)  # or redirect to their respective dashboard
    return render_template('dashboard/customer/dashboard.html')


@dashboard.route('/customer/profile', methods=['GET', 'POST'])
@login_required
def customer_profile():

    # What is the below if statement for?
    if current_user.role != 'customer':
        flash("Access denied: Only customers can access this page.", 'danger')
        return redirect(url_for('dashboard.customer_dashboard'))
    # What is the above if statement for?

    customer = current_user.customer

    customer_profile_form = CustomerProfileForm()

    country_choices = current_app.config['CUSTOMER_COUNTRIES']
    customer_profile_form.country.choices = [('', '-- Select country --')] + [(c.alpha_2, c.name) for c in countries if c.alpha_2 in country_choices]

    if customer_profile_form.validate_on_submit():

        customer.phone_number = customer_profile_form.phone_number.data
        customer.address_line1 = customer_profile_form.address_line1.data
        customer.address_line2 = customer_profile_form.address_line2.data
        customer.city = customer_profile_form.city.data
        customer.state = customer_profile_form.state.data
        customer.postcode = customer_profile_form.postcode.data
        customer.country = customer_profile_form.country.data

        customer.profile_complete = True

        db.session.commit()

        flash('Your profile has been updated successfully.', 'success')
        return redirect(url_for('dashboard.customer_dashboard'))
    
    else:
        customer_profile_form.process(obj = current_user.customer) # Populating the form has some bad effects on post update

    # ❗ Note the full path relative to `templates/`
    return render_template('dashboard/customer/profile.html', form = customer_profile_form)



@dashboard.route('/supplier')
@login_required
def supplier_dashboard():
    if current_user.role != 'supplier':
        abort(403)  # or redirect to their respective dashboard

    return render_template('dashboard/supplier/dashboard.html')



@dashboard.route('/supplier/verification', methods=['GET', 'POST'])
@login_required
def supplier_verification():
    if current_user.role != 'supplier':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.supplier_dashboard'))

    supplier = current_user.supplier
    supplier_verification_form = SupplierVerificationForm()

    supplier_verification_form.reg_country.choices = [('', '-- Select country --')] + [(c.alpha_2, c.name) for c in countries if c.alpha_2]

    op_country_choices = current_app.config['SUPPLIER_COUNTRIES']
    supplier_verification_form.op_country.choices = [('', '-- Select country --')] + [(c.alpha_2, c.name) for c in countries if c.alpha_2 in op_country_choices]

    if supplier_verification_form.validate_on_submit():

        # Business Details
        supplier.business_name = supplier_verification_form.business_name.data
        supplier.company_registration_number = supplier_verification_form.company_registration_number.data
        supplier.nature_of_business = supplier_verification_form.nature_of_business.data
        supplier.tax_id_number = supplier_verification_form.tax_id_number.data

        # Director Details
        supplier.director_name = supplier_verification_form.director_name.data

        # Contact Person - Primary
        supplier.contact_name = supplier_verification_form.contact_name.data
        supplier.contact_designation = supplier_verification_form.contact_designation.data
        supplier.contact_email = supplier_verification_form.contact_email.data
        supplier.contact_phone = supplier_verification_form.contact_phone.data

        # Contact Person - Alternate (optional)
        supplier.alt_contact_name = supplier_verification_form.alt_contact_name.data
        supplier.alt_contact_designation = supplier_verification_form.alt_contact_designation.data
        supplier.alt_contact_email = supplier_verification_form.alt_contact_email.data
        supplier.alt_contact_phone = supplier_verification_form.alt_contact_phone.data

        # Address - Registered
        supplier.reg_address_line1 = supplier_verification_form.reg_address_line1.data
        supplier.reg_address_line2 = supplier_verification_form.reg_address_line2.data
        supplier.reg_city = supplier_verification_form.reg_city.data
        supplier.reg_state = supplier_verification_form.reg_state.data
        supplier.reg_postcode = supplier_verification_form.reg_postcode.data
        supplier.reg_country = supplier_verification_form.reg_country.data

        # Address - Operational
        supplier.op_address_line1 = supplier_verification_form.op_address_line1.data
        supplier.op_address_line2 = supplier_verification_form.op_address_line2.data
        supplier.op_city = supplier_verification_form.op_city.data
        supplier.op_state = supplier_verification_form.op_state.data
        supplier.op_postcode = supplier_verification_form.op_postcode.data
        supplier.op_country = supplier_verification_form.op_country.data


        # Bank Details
        supplier.bank_name = supplier_verification_form.bank_name.data
        supplier.bank_account_number = supplier_verification_form.bank_account_number.data

        # Metadata
        supplier.date_joined = db.func.current_timestamp()

        supplier.country_code = supplier_verification_form.op_country.data

        # Verification workflow
        supplier.status = SupplierStatus.SUBMITTED
        supplier.submitted_at = db.func.current_timestamp()


        # Uploaded files
        files = {
            "registration_cert": supplier_verification_form.registration_cert.data,
            "bank_verification_doc": supplier_verification_form.bank_verification_doc.data,
            "director_id_doc": supplier_verification_form.director_id_doc.data,
        }

        for kind, f in files.items():
            if f and f.filename:
                upsert_supplier_doc(supplier.id, kind, f, delete_old_local=True)

        db.session.commit()

        flash('Verification details submitted successfully.', 'success')
        return redirect(url_for('dashboard.supplier_dashboard'))
    
    else:
        supplier_verification_form.process(obj = current_user.supplier)
    
    # Do we need supplier = supplier? I don't think we are passing supplier into form?
    return render_template('dashboard/supplier/verification.html', form=supplier_verification_form, supplier=supplier)



# app/dashboard/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import dashboard
from ..extensions import db
from ..models import Product, ProductStatus
from .forms import AddProductForm
from werkzeug.utils import secure_filename
import re, os

def _slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\- ]+", "", text).strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:220] or None

def _unique_slug(base: str) -> str:
    """Generate a unique slug for Product.slug."""
    slug = base
    if not slug:
        slug = "product"
    original = slug
    i = 2
    while Product.query.filter_by(slug=slug).first():
        slug = f"{original}-{i}"
        i += 1
    return slug


@dashboard.route("/supplier/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    # guard: suppliers only
    if current_user.role != "supplier":
        flash("Only suppliers can add products.", "danger")
        return redirect(url_for("main.index"))

    form = AddProductForm()
    if form.validate_on_submit():
        # NOTE: we’re saving as DRAFT first.
        product = Product(
            supplier_id=current_user.supplier.id,
            name=form.name.data,
            short_desc=form.short_desc.data,
            description=form.description.data,
            category=form.category.data,
            subcategory=form.subcategory.data,
            hs_code=form.hs_code.data,
            country_of_origin=(form.country_of_origin.data or "").upper() or None,
            price=form.price.data,
            currency=form.currency.data,
            moq=form.moq.data or 1,
            stock=form.stock.data or 0,
            lead_time_days=form.lead_time_days.data,
            incoterms=form.incoterms.data or None,
            status=ProductStatus.DRAFT,
            is_deleted=False,
        )

        # slug
        base_slug = _slugify(form.name.data)
        product.slug = _unique_slug(base_slug)

        # Upload to database
        db.session.add(product)
        db.session.commit()

        # Optional: if Publish pressed, check requirements & mark LIVE
        if form.publish.data:
            missing = []
            # if not product.main_image_path:
            #     missing.append("At least one image")
            if not current_user.supplier.is_verified:
                missing.append("Supplier verification")

            if missing:
                flash("Saved as draft. To publish, please add: " + ", ".join(missing), "warning")
            else:
                product.status = ProductStatus.LIVE
                db.session.commit()
                flash("Product published!", "success")
                return redirect(url_for("dashboard.supplier_products"))

        flash("Product saved as draft.", "success")
        return redirect(url_for("dashboard.supplier_products"))

    return render_template("dashboard/supplier/add_product.html", form=form)


# @dashboard.route("/supplier/add_product", methods=["GET", "POST"])
# @login_required
# def add_product():
#     if current_user.role != 'supplier':
#         flash("Only suppliers can add products.", "error")
#         return redirect(url_for("main.index"))

#     add_product_form = AddProductForm()

#     if add_product_form.validate_on_submit():
#         supplier = current_user.supplier

#         # Product is active only if supplier is verified
#         if supplier.status == SupplierStatus.APPROVED: is_active = True

#         # Handle image upload
#         image_filename = None
#         if add_product_form.image.data:
#             filename = secure_filename(add_product_form.image.data.filename)
#             image_path = os.path.join("app/static/uploads/products", filename)
#             add_product_form.image.data.save(image_path)
#             image_filename = filename

#         product = Product(
#             supplier_id=supplier.id,
#             name=add_product_form.name.data,
#             description=add_product_form.description.data,
#             price=add_product_form.price.data,
#             stock=add_product_form.stock.data,
#             image_path=image_filename,
#             is_active=is_active
#         )

#         db.session.add(product)
#         db.session.commit()

#         if is_active:
#             flash("Product added successfully and is now live!", "success")
#         else:
#             flash("Product added but will go live once you are verified.", "warning")

#         return redirect(url_for("dashboard.supplier_dashboard"))

#     return render_template(
#         "dashboard/supplier/add_product.html",
#         form=add_product_form
#     )



@dashboard.route("/supplier/products")
@login_required
def supplier_products():
    if current_user.role != "supplier":
        abort(403)
    page = request.args.get("page", 1, type=int)
    q = (Product.query
         .filter_by(supplier_id=current_user.supplier.id, is_deleted=False)
         .order_by(Product.created_at.desc()))
    products = q.paginate(page=page, per_page=10, error_out=False)
    return render_template("dashboard/supplier/products.html", products=products)

@dashboard.route("/supplier/products/<int:product_id>/toggle", methods=["POST"])
@login_required
def supplier_product_toggle(product_id):
    if current_user.role != "supplier":
        abort(403)
    p = Product.query.filter_by(id=product_id,
                                supplier_id=current_user.supplier.id,
                                is_deleted=False).first_or_404()

    # flip LIVE <-> DRAFT (you can add more rules, e.g. require image & verified supplier)
    if p.status == ProductStatus.LIVE:
        p.status = ProductStatus.DRAFT
        flash("Product unpublished.", "info")
    else:
        # simple publish rule; expand later (image present, supplier verified, etc.)
        if not current_user.supplier.status == SupplierStatus.APPROVED:
            flash("You must be verified before publishing products.", "warning")
        # elif not p.main_image_path:
        #     flash("Add a product image before publishing.", "warning")
        else:
            p.status = ProductStatus.LIVE
            flash("Product published.", "success")

    db.session.commit()
    return redirect(url_for("dashboard.supplier_products", page=request.args.get("page", 1)))

@dashboard.route("/supplier/products/<int:product_id>/delete", methods=["POST"])
@login_required
def supplier_product_delete(product_id):
    if current_user.role != "supplier":
        abort(403)
    p = Product.query.filter_by(id=product_id,
                                supplier_id=current_user.supplier.id,
                                is_deleted=False).first_or_404()
    p.is_deleted = True
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("dashboard.supplier_products", page=request.args.get("page", 1)))



# # LIST: /dashboard/supplier/products
# @dashboard.route("/supplier/products")
# @login_required
# def supplier_products():
#     if not hasattr(current_user, "supplier"):
#         abort(403)

#     page = request.args.get("page", 1, type=int)
#     per_page = 10

#     products = (
#         Product.query
#         .filter_by(supplier_id=current_user.supplier.id)
#         .order_by(Product.created_at.desc())
#         .paginate(page=page, per_page=per_page, error_out=False)
#     )

#     return render_template("dashboard/supplier/products.html", products=products)

# # TOGGLE PUBLISH (publish/unpublish)
# @dashboard.route("/supplier/products/<int:product_id>/toggle", methods=["POST"])
# @login_required
# def supplier_product_toggle(product_id):
#     if not hasattr(current_user, "supplier"):
#         abort(403)

#     product = Product.query.get_or_404(product_id)
#     if product.supplier_id != current_user.supplier.id:
#         abort(403)

#     # Only allow publishing if supplier is verified
#     if not current_user.supplier.is_verified and not product.is_active:
#         flash("You must be verified before publishing products.", "warning")
#         return redirect(url_for("dashboard.supplier_products"))

#     product.is_active = not product.is_active
#     db.session.commit()
#     flash(("Product is now LIVE!" if product.is_active else "Product unpublished."), "success")
#     return redirect(url_for("dashboard.supplier_products"))

# # DELETE product (simple demo-safe version; switch to a CSRF-protected form in production)
# @dashboard.route("/supplier/products/<int:product_id>/delete", methods=["POST"])
# @login_required
# def supplier_product_delete(product_id):
#     if not hasattr(current_user, "supplier"):
#         abort(403)

#     product = Product.query.get_or_404(product_id)
#     if product.supplier_id != current_user.supplier.id:
#         abort(403)

#     db.session.delete(product)
#     db.session.commit()
#     flash("Product deleted.", "success")
#     return redirect(url_for("dashboard.supplier_products"))
