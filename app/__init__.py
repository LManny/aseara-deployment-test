from flask import Flask
from .extensions import db, migrate, login_manager
from datetime import datetime
from .cart.cart_utils import cart_count  # adjust import path if needed


def create_app():

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .main import main  # import the blueprint object
    app.register_blueprint(main)  # register the blueprint

    from .auth import auth  # import the blueprint object
    app.register_blueprint(auth, url_prefix='/auth')  # register the blueprint

    from .dashboard import dashboard  # import the blueprint object
    app.register_blueprint(dashboard, url_prefix='/dashboard')  # register the blueprint

    from .catalog import catalog  # import the blueprint object
    app.register_blueprint(catalog, url_prefix='/catalog')  # register the blueprint

    from .cart import cart  # import the blueprint object
    app.register_blueprint(cart, url_prefix='/cart')  # register the blueprint

    from .admin import admin  # import the blueprint object
    app.register_blueprint(admin, url_prefix='/admin')  # register the blueprint

    @app.context_processor
    def inject_globals():
        return {
            "cart_items_count": cart_count(),                # badge number
            "current_year": datetime.utcnow().year,          # footer year
        }

    return app


from .models import User
#What tf is this for?
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))