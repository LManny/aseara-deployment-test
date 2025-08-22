from flask import render_template, flash, abort, request, redirect, url_for
from . import cart #this imports that main blueprint from __init__.py

from app.extensions import db

from app.models import Product, ProductStatus, Supplier, SupplierStatus
from flask_login import login_required, current_user

from .form import AddToCartForm
from .cart_utils import add_to_cart, cart_items_with_products, update_qty, remove_item, clear_cart

from sqlalchemy import or_, and_, func


@cart.route("/", methods=["GET", "POST"])
@cart.route("/view", methods=["GET", "POST"])
def view():
    # Handle inline updates (quantity inputs)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update":
            # Expect multiple qty fields named: qty-<product_id>
            for k, v in request.form.items():
                if k.startswith("qty-"):
                    try:
                        pid = int(k.split("-", 1)[1])
                        qty = int(v or 0)
                        update_qty(pid, qty)
                    except ValueError:
                        continue
            flash("Cart updated.", "success")
            return redirect(url_for("catalog.cart"))
        elif action == "remove":
            pid = request.form.get("product_id")
            if pid and pid.isdigit():
                remove_item(int(pid))
                flash("Item removed.", "success")
            return redirect(url_for("catalog.cart"))
        elif action == "clear":
            clear_cart()
            flash("Cart cleared.", "success")
            return redirect(url_for("cart.cart"))

    items, totals = cart_items_with_products()
    return render_template("cart/cart.html", items=items, totals=totals)



# COUNTRY_NAMES = {
#     "MY": "Malaysia", "SG": "Singapore", "TH": "Thailand", "ID": "Indonesia",
#     "PH": "Philippines", "VN": "Vietnam", "BN": "Brunei", "KH": "Cambodia",
#     "LA": "Laos", "MM": "Myanmar", "TL": "Timor-Leste"
# }

# def normalize_cc(code: str) -> str:
#     return (code or "").strip().upper()