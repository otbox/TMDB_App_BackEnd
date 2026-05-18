from flask import Flask
from .extensions import db, cors, jwt
from datetime import timedelta



def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ratings.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "change-this-super-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"]  = timedelta(minutes=30)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    db.init_app(app)


    cors.init_app(app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type", "Authorization"]
    )

    jwt.init_app(app)

    from .routes.users import users_bp
    from .routes.ratings import ratings_bp

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(ratings_bp, url_prefix="/api")

    with app.app_context():
        from .models import User, Rating
        db.create_all()

    return app