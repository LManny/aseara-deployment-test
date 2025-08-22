# app/catalog/cart_utils.py
from flask import session
from decimal import Decimal
from ..models import Product

CART_KEY = "cart"  # { "product_id": quantity }

def get_cart():
    return session.get(CART_KEY, {})

def set_cart(cart):
    session[CART_KEY] = cart

def add_to_cart(product_id: int, qty: int):
    cart = get_cart()
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + int(qty)
    set_cart(cart)

def update_qty(product_id: int, qty: int):
    cart = get_cart()
    pid = str(product_id)
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = int(qty)
    set_cart(cart)

def remove_item(product_id: int):
    cart = get_cart()
    cart.pop(str(product_id), None)
    set_cart(cart)

def clear_cart():
    set_cart({})

def cart_count():
    return sum(get_cart().values())

def cart_items_with_products():
    """
    Returns (items, totals) where:
      items = [ { 'product': Product, 'qty': int, 'line_total': Decimal }, ... ]
      totals = { 'subtotal': Decimal }
    """
    cart = get_cart()
    pids = [int(pid) for pid in cart.keys()]
    items = []
    if not pids:
        return items, {"subtotal": Decimal("0.00")}

    products = Product.query.filter(Product.id.in_(pids), Product.is_deleted == False).all()
    product_map = {p.id: p for p in products}
    subtotal = Decimal("0.00")

    for pid_str, qty in cart.items():
        pid = int(pid_str)
        p = product_map.get(pid)
        if not p:
            continue
        line_total = (p.price or Decimal("0.00")) * int(qty)
        subtotal += line_total
        items.append({"product": p, "qty": int(qty), "line_total": line_total})

    return items, {"subtotal": subtotal}
