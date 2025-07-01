import os
from flask import Flask
from .extensions import db
from config import DevConfig, ProdConfig, TestConfig, PytestConfig
from dotenv import load_dotenv
from .routes.record import transcribe_bp
from .routes.auth import auth_bp
from .extensions import jwt
from .oauth import init_oauth
from .routes.google_auth import google_auth_bp
from .routes.view_records import view_records_bp
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

migrate = Migrate(compare_type=True)
load_dotenv()


def create_app():
    env = os.getenv("FLASK_ENV", "dev")

    config_map = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig,
        "pytest": PytestConfig
    }

    app = Flask(__name__)
    app.config.from_object(config_map.get(env, DevConfig))
    
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    init_oauth(app)

    from . import models # Makes models known to alembic.

    if app.config["TESTING"]:
        with app.app_context():
            db.reflect()
            db.drop_all()
            db.create_all()

    app.register_blueprint(transcribe_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth") # adding prefix to distinguish backend routes from frontend.
    app.register_blueprint(google_auth_bp, url_prefix="/api/oauth/google")
    app.register_blueprint(view_records_bp)

    return app
