from flask import render_template, redirect, url_for, abort, flash, request
from flask_login import login_required, current_user
from . import dashboard
from .forms import CustomerProfileForm, SupplierVerificationForm, AddProductForm
from app.models import Customer, Supplier, Product
from app.extensions import db

from flask import current_app
from werkzeug.utils import secure_filename
import os


@dashboard.route('/')
@login_required
def user_dashboard():
    if current_user.role == 'customer':
        return redirect(url_for('dashboard.customer_dashboard'))
    elif current_user.role == 'supplier':
        return redirect(url_for('dashboard.supplier_dashboard'))
    return redirect(url_for('main.index'))


@dashboard.route('/customer')
@login_required
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

    # form = CustomerProfileForm(obj=customer) # What is the obj=customer for? -- this apparently populates the form with default values
    customer_profile_form = CustomerProfileForm()

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
    supplier_verification_form = SupplierVerificationForm(obj=supplier) # Let's try and use obj = supplier

    if supplier_verification_form.validate_on_submit():

        # supplier_verification_form.populate_obj(supplier) # This sets default values?

        supplier.business_name = supplier_verification_form.business_name.data
        supplier.company_registration_number = supplier_verification_form.company_registration_number.data
        supplier.nature_of_business = supplier_verification_form.nature_of_business.data
        supplier.tax_id_number = supplier_verification_form.tax_id_number.data

        supplier.director_name = supplier_verification_form.director_name.data

        supplier.contact_name = supplier_verification_form.contact_name.data
        supplier.contact_designation = supplier_verification_form.contact_designation.data
        supplier.contact_email = supplier_verification_form.contact_email.data
        supplier.contact_phone = supplier_verification_form.contact_phone.data

        supplier.alt_contact_name = supplier_verification_form.alt_contact_name.data
        supplier.alt_contact_designation = supplier_verification_form.alt_contact_designation.data
        supplier.alt_contact_email = supplier_verification_form.alt_contact_email.data
        supplier.alt_contact_phone = supplier_verification_form.alt_contact_phone.data

        supplier.reg_address_line1 = supplier_verification_form.reg_address_line1.data
        supplier.reg_address_line2 = supplier_verification_form.reg_address_line2.data
        supplier.reg_city = supplier_verification_form.reg_city.data
        supplier.reg_state = supplier_verification_form.reg_state.data
        supplier.reg_postcode = supplier_verification_form.reg_postcode.data
        supplier.reg_country = supplier_verification_form.reg_country.data

        supplier.op_address_line1 = supplier_verification_form.op_address_line1.data
        supplier.op_address_line2 = supplier_verification_form.op_address_line2.data
        supplier.op_city = supplier_verification_form.op_city.data
        supplier.op_state = supplier_verification_form.op_state.data
        supplier.op_postcode = supplier_verification_form.op_postcode.data
        supplier.op_country = supplier_verification_form.op_country.data

        supplier.bank_name = supplier_verification_form.bank_name.data
        supplier.bank_account_number = supplier_verification_form.bank_account_number.data

        # # How are we going to store these documents?
        # supplier.registration_cert_path = db.Column(db.String(255))  # Company cert
        # supplier.bank_verification_doc_path = db.Column(db.String(255))  # Bank letter/statement
        # supplier.director_id_doc_path = db.Column(db.String(255))  # NRIC/Passport

        supplier.profile_complete = True
        db.session.commit()
        # We need to somehow add a mechanism for ASEARA team members to verify these suppliers and set supplier.is_verified = True

        flash('Verification details submitted successfully.', 'success')
        return redirect(url_for('dashboard.supplier_dashboard'))
    
    # Do we need supplier = supplier? I don't think we are passing supplier into form?
    return render_template('dashboard/supplier/verification.html', form=supplier_verification_form, supplier=supplier)




@dashboard.route("/supplier/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if not hasattr(current_user, 'supplier'):
        flash("Only suppliers can add products.", "error")
        return redirect(url_for("main.index"))

    add_product_form = AddProductForm()

    if add_product_form.validate_on_submit():
        supplier = current_user.supplier

        # Product is active only if supplier is verified
        is_active = supplier.is_verified

        # Handle image upload
        image_filename = None
        if add_product_form.image.data:
            filename = secure_filename(add_product_form.image.data.filename)
            image_path = os.path.join("app/static/uploads/products", filename)
            add_product_form.image.data.save(image_path)
            image_filename = filename

        product = Product(
            supplier_id=supplier.id,
            name=add_product_form.name.data,
            description=add_product_form.description.data,
            price=add_product_form.price.data,
            stock=add_product_form.stock.data,
            image_path=image_filename,
            is_active=is_active
        )

        db.session.add(product)
        db.session.commit()

        if is_active:
            flash("Product added successfully and is now live!", "success")
        else:
            flash("Product added but will go live once you are verified.", "warning")

        return redirect(url_for("dashboard.supplier_dashboard"))

    return render_template(
        "dashboard/supplier/add_product.html",
        form=add_product_form
    )


# LIST: /dashboard/supplier/products
@dashboard.route("/supplier/products")
@login_required
def supplier_products():
    if not hasattr(current_user, "supplier"):
        abort(403)

    page = request.args.get("page", 1, type=int)
    per_page = 10

    products = (
        Product.query
        .filter_by(supplier_id=current_user.supplier.id)
        .order_by(Product.date_added.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template("dashboard/supplier/products.html", products=products)

# TOGGLE PUBLISH (publish/unpublish)
@dashboard.route("/supplier/products/<int:product_id>/toggle", methods=["POST"])
@login_required
def supplier_product_toggle(product_id):
    if not hasattr(current_user, "supplier"):
        abort(403)

    product = Product.query.get_or_404(product_id)
    if product.supplier_id != current_user.supplier.id:
        abort(403)

    # Only allow publishing if supplier is verified
    if not current_user.supplier.is_verified and not product.is_active:
        flash("You must be verified before publishing products.", "warning")
        return redirect(url_for("dashboard.supplier_products"))

    product.is_active = not product.is_active
    db.session.commit()
    flash(("Product is now LIVE!" if product.is_active else "Product unpublished."), "success")
    return redirect(url_for("dashboard.supplier_products"))

# DELETE product (simple demo-safe version; switch to a CSRF-protected form in production)
@dashboard.route("/supplier/products/<int:product_id>/delete", methods=["POST"])
@login_required
def supplier_product_delete(product_id):
    if not hasattr(current_user, "supplier"):
        abort(403)

    product = Product.query.get_or_404(product_id)
    if product.supplier_id != current_user.supplier.id:
        abort(403)

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("dashboard.supplier_products"))
