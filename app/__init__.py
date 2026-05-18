from flask import Flask
from .extensions import db, cors, jwt

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ratings.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "change-this-super-secret-key"

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
    jwt.init_app(app)

    from .routes.users import users_bp
    from .routes.ratings import ratings_bp

    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(ratings_bp, url_prefix="/api")

    with app.app_context():
        from .models import User, Rating
        db.create_all()

    return app