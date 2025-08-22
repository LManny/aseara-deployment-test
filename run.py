from app import create_app

app = create_app()

from flask import session, current_app

@app.context_processor
def inject_globals():
    # countries list (trim as you like)
    COUNTRIES = [
        {"code":"MY","name":"Malaysia"},
        {"code":"SG","name":"Singapore"},
        {"code":"TH","name":"Thailand"},
        {"code":"ID","name":"Indonesia"},
        {"code":"PH","name":"Philippines"},
        {"code":"VN","name":"Vietnam"},
        {"code":"KH","name":"Cambodia"},
        {"code":"LA","name":"Laos"},
        {"code":"MM","name":"Myanmar"},
        {"code":"BN","name":"Brunei"},
        {"code":"TL","name":"Timor-Leste"},
    ]

    # cart badge
    cart = session.get("cart", {})
    cart_count = 0
    if isinstance(cart, dict):
        for item in cart.values():
            try:
                cart_count += int(item.get("qty", 0))
            except Exception:
                pass

    # expose whether a 'cart' blueprint exists
    has_cart = "cart" in current_app.blueprints

    return {"COUNTRIES": COUNTRIES, "cart_count": cart_count, "has_cart": has_cart}



if __name__ == '__main__':
    app.run(debug=True)