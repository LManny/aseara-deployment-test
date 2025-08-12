from flask import Flask
from .extensions import db, migrate, login_manager


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

    # Add health check route here ⬇
    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}, 200


    return app


from .models import User
#What tf is this for?
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))