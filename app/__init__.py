from flask import Flask
from .extensions import db, cors, jwt
from datetime import timedelta
import os

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:8080"
    ).split(",")
    if origin.strip()
]

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ratings.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-this-super-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    db.init_app(app)

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": ALLOWED_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type", "Authorization"]
    )

    jwt.init_app(app)

    from .routes.users import users_bp
    from .routes.ratings import ratings_bp
    from .routes.episode_ratings import episode_ratings_bp

    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(ratings_bp, url_prefix="/api")
    app.register_blueprint(episode_ratings_bp, url_prefix="/api")

    with app.app_context():
        from .models import User, Rating, EpisodeRating
        db.create_all()

    return app
