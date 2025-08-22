from flask import render_template, flash, abort, request, redirect, url_for
from . import catalog #this imports that main blueprint from __init__.py

from app.extensions import db

from app.models import Product, ProductStatus, Supplier, SupplierStatus
from flask_login import login_required, current_user

from .form import AddToCartForm
from app.cart.cart_utils import add_to_cart, cart_items_with_products, update_qty, remove_item, clear_cart

from sqlalchemy import or_, and_, func


@catalog.route("/search")
def search():
    # read filters
    q = (request.args.get("q") or "").strip()
    country = (request.args.get("country") or "").strip().upper()
    category = (request.args.get("category") or "").strip()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = (request.args.get("sort") or "").strip().lower()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # base query: LIVE, not deleted, supplier APPROVED
    qry = (
        Product.query
        .join(Supplier, Supplier.id == Product.supplier_id)
        .filter(
            Product.is_deleted.is_(False),
            Product.status == ProductStatus.LIVE,
            Supplier.status == SupplierStatus.APPROVED
        )
    )

    # text search
    if q:
        like = f"%{q}%"
        qry = qry.filter(or_(
            Product.name.ilike(like),
            Product.short_desc.ilike(like),
            Product.description.ilike(like),
        ))

    # filters
    if country:
        qry = qry.filter(
            or_(
                Product.country_of_origin == country,
                Supplier.country_code == country,     # optional fallback
                Supplier.reg_country == country       # optional fallback
            )
        )

    if category:
        qry = qry.filter(or_(
            Product.category == category,
            Product.subcategory == category
        ))

    if min_price is not None:
        qry = qry.filter(Product.price >= min_price)
    if max_price is not None:
        qry = qry.filter(Product.price <= max_price)

    # sorting
    if sort == "newest":
        qry = qry.order_by(Product.created_at.desc())
    elif sort == "price_asc":
        qry = qry.order_by(Product.price.asc())
    elif sort == "price_desc":
        qry = qry.order_by(Product.price.desc())
    elif sort == "name":
        qry = qry.order_by(Product.name.asc())
    else:
        qry = qry.order_by(Product.created_at.desc())  # sensible default

    products = qry.paginate(page=page, per_page=per_page, error_out=False)

    current_filters = {
        "q": q,
        "country": country,
        "category": category,
        "min_price": "" if min_price is None else min_price,
        "max_price": "" if max_price is None else max_price,
        "sort": sort,
    }

    return render_template(
        "catalog/search_results.html",
        products=products,
        current_filters=current_filters,
    )


@catalog.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):
    product = Product.query.filter_by(id=product_id, is_deleted=False).first_or_404()

    # Only show live products to the public; allow owner to preview drafts
    if product.status != ProductStatus.LIVE:
        can_preview = current_user.is_authenticated and getattr(current_user, "supplier", None)
        if not (can_preview and current_user.supplier.id == product.supplier_id):
            abort(404)

    form = AddToCartForm()
    if request.method == "GET":
        form.product_id.data = str(product.id)
        form.quantity.data = max(product.moq or 1, 1)

    if form.validate_on_submit():
        # re-check product exists & purchasable
        if product.status != ProductStatus.LIVE or product.is_deleted:
            flash("This product is not available.", "warning")
            return redirect(url_for("catalog.product_detail", product_id=product.id))

        qty = form.quantity.data or 1
        # Optional stock guard:
        if product.stock is not None and product.stock >= 0 and qty > product.stock:
            flash("Requested quantity exceeds available stock.", "warning")
            return redirect(url_for("catalog.product_detail", product_id=product.id))

        # respect MOQ
        if product.moq and qty < product.moq:
            qty = product.moq

        add_to_cart(product.id, qty)
        flash("Added to cart.", "success")
        # redirect here to product page (or a /cart page once you build it)
        return redirect(url_for("catalog.product_detail", product_id=product.id))

    return render_template("catalog/product_detail.html", product=product, form=form)


COUNTRY_NAMES = {
    "MY": "Malaysia", "SG": "Singapore", "TH": "Thailand", "ID": "Indonesia",
    "PH": "Philippines", "VN": "Vietnam", "BN": "Brunei", "KH": "Cambodia",
    "LA": "Laos", "MM": "Myanmar", "TL": "Timor-Leste"
}

def normalize_cc(code: str) -> str:
    return (code or "").strip().upper()

@catalog.route("/c/<country_code>")
def country(country_code):
    cc = normalize_cc(country_code)
    name = COUNTRY_NAMES.get(cc)
    if not name:
        abort(404)

    # Featured products (LIVE only)
    featured = (Product.query
        .filter(Product.country_of_origin == cc,
                Product.status == ProductStatus.LIVE,
                Product.is_deleted == False)
        .order_by(Product.created_at.desc())
        .limit(12).all())

    # Category counts (for quick nav)
    cat_counts = (Product.query
        .with_entities(Product.category, func.count(Product.id))
        .filter(Product.country_of_origin == cc,
                Product.status == ProductStatus.LIVE,
                Product.is_deleted == False)
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
        .limit(12)
        .all())

    # Not strictly needed, but nice: “featured suppliers”
    suppliers = (Supplier.query
        .join(Product, Product.supplier_id == Supplier.id)
        .filter(Product.country_of_origin == cc,
                Product.status == ProductStatus.LIVE,
                Product.is_deleted == False)
        .distinct()
        .limit(8).all())

    return render_template(
        "catalog/country.html",
        cc=cc, country_name=name,
        featured_products=featured,
        category_counts=cat_counts,
        suppliers=suppliers
    )

@catalog.route("/c/<country_code>/category/<category>")
def country_category(country_code, category):
    cc = normalize_cc(country_code)
    name = COUNTRY_NAMES.get(cc)
    if not name:
        abort(404)

    page = request.args.get("page", 1, type=int)
    q = (Product.query
         .filter(Product.country_of_origin == cc,
                 Product.category == category,
                 Product.status == ProductStatus.LIVE,
                 Product.is_deleted == False)
         .order_by(Product.created_at.desc()))
    products = q.paginate(page=page, per_page=24, error_out=False)

    return render_template(
        "catalog/country_category.html",
        cc=cc, country_name=name, category=category,
        products=products
    )
