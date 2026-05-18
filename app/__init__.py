from flask import Flask
from .extensions import db, cors

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ratings.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    cors.init_app(app)

    from .routes.ratings import ratings_bp
    app.register_blueprint(ratings_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app