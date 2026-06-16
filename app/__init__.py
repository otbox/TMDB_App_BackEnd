from flask import Flask, request
from .extensions import db, cors, jwt
from datetime import timedelta
import os

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:8080"
).split(",")


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ratings.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "change-this-super-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    db.init_app(app)

    cors.init_app(app,
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

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(ratings_bp, url_prefix="/api")
    app.register_blueprint(episode_ratings_bp, url_prefix="/api")

    with app.app_context():
        from .models import User, Rating, EpisodeRating
        db.create_all()

    return app
