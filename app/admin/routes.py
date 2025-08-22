from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.security import role_required
from app.models import User, Supplier, SupplierStatus
from app.extensions import db
from .forms import VerificationFilterForm, VerificationActionForm
from . import admin

COUNTRIES = [
    ("MY", "Malaysia"),
    ("SG", "Singapore"),
    ("TH", "Thailand"),
    ("ID", "Indonesia"),
    ("PH", "Philippines"),
    ("VN", "Vietnam"),
    ("BN", "Brunei"),
    ("KH", "Cambodia"),
    ("LA", "Laos"),
    ("MM", "Myanmar"),
    ("TL", "Timor-Leste"),
]


@admin.route("/dashboard")
@login_required
@role_required('admin')
def dashboard():
    return render_template("admin/dashboard.html")


@admin.route("/verification_queue", methods=["GET"])
@login_required
@role_required('admin')
def verification_queue():
    form = VerificationFilterForm(request.args)
    # country field only for global admin (hide/ignore for country_admin)
    if current_user.role == "admin":
        form.country.choices = [("", "All")] + COUNTRIES
    else:
        form.country.choices = [("", "All")]

    q = Supplier.query

    # scope by country for country_admins
    if current_user.role == "country_admin" and current_user.country_code:
        q = q.filter(Supplier.reg_country == current_user.country_code.upper())

    # read normalized values from form
    search = (form.q.data or "").strip()
    status_str = (form.status.data or "").strip()
    country = (form.country.data or "").strip().upper()

    # status default: submitted + under_review
    if status_str:
        try:
            q = q.filter(Supplier.status == SupplierStatus(status_str))
        except ValueError:
            pass
    else:
        q = q.filter(Supplier.status.in_([SupplierStatus.SUBMITTED, SupplierStatus.UNDER_REVIEW]))

    if current_user.role == "admin" and country:
        q = q.filter(Supplier.reg_country == country)

    if search:
        like = f"%{search}%"
        q = q.join(User).filter(or_(
            Supplier.business_name.ilike(like),
            Supplier.company_registration_number.ilike(like),
            User.email.ilike(like),
        ))

    suppliers = q.order_by(Supplier.submitted_at.desc().nullslast(), Supplier.id.desc()).all()

    action_form = VerificationActionForm()  # for inline row actions

    return render_template(
        "admin/verification_queue.html",
        form=form,                # pass the form
        suppliers=suppliers,
        countries=COUNTRIES,      # only needed if your template still uses it elsewhere
        action_form=action_form
    )



@admin.route("/verification/<int:supplier_id>", methods=["GET", "POST"])
@login_required
def verification_detail(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    form = VerificationActionForm()

    if form.validate_on_submit():
        if form.approve.data:
            supplier.status = SupplierStatus.APPROVED
            flash(f"{supplier.business_name or 'Supplier'} approved.", "success")
        elif form.needs_more_info.data:
            supplier.status = SupplierStatus.NEEDS_MORE_INFO
            flash(f"{supplier.business_name or 'Supplier'} marked as needs more info.", "warning")
        elif form.reject.data:
            supplier.status = SupplierStatus.REJECTED
            flash(f"{supplier.business_name or 'Supplier'} rejected.", "danger")
        db.session.commit()
        return redirect(url_for("admin.verification_queue"))

    return render_template("admin/verification_detail.html", supplier=supplier, form=form)



# @admin.route("/verification_queue")
# @login_required
# @role_required('admin')
# def verification_queue():
#     # base query
#     q = Supplier.query

#     # scope for country_admins (global admin sees all)
#     if current_user.admin.admin_type == "country" and current_user.admin.country_code:
#         q = q.filter(Supplier.op_country == current_user.admin.country_code.upper())

#     # read filters
#     search = (request.args.get("q") or "").strip()
#     status_str = (request.args.get("status") or "").strip()
#     country = (request.args.get("country") or "").strip().upper()

#     # status filter: default to submitted + under_review if not explicitly set
#     print(status_str)
#     if status_str:
#         try:
#             status_enum = SupplierStatus(status_str)
#         except ValueError:
#             status_enum = None
#         if status_enum:
#             q = q.filter(Supplier.status == status_enum)
#     else:
#         q = q.filter(Supplier.status.in_([SupplierStatus.SUBMITTED, SupplierStatus.UNDER_REVIEW]))

#     for x in q: print(x.op_country, x.user.email)

#     # country filter (admins only, but harmless if present for country_admins)
#     if country:
#         q = q.filter(Supplier.country_code == country)

#     # search by business name, reg no, or user email
#     if search:
#         like = f"%{search}%"
#         q = q.join(User).filter(or_(
#             Supplier.business_name.ilike(like),
#             Supplier.company_registration_number.ilike(like),
#             User.email.ilike(like),
#         ))

#     # order: newest submissions first, then id desc
#     q = q.order_by(Supplier.submitted_at.desc().nullslast(), Supplier.id.desc())

#     # pagination
#     page = request.args.get("page", 1, type=int)
#     per_page = 20
#     pagination = q.paginate(page=page, per_page=per_page, error_out=False)
#     print(pagination.items)

#     return render_template(
#         "admin/verification_queue.html",
#         suppliers=pagination.items,
#         pagination=pagination,
#         countries=COUNTRIES,
#     )