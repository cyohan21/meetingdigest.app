import os
import pytest
from app import create_app
from app.extensions import db
from config import PytestConfig
from flask_jwt_extended import create_access_token
from app.models import User

# Ensure secrets are available for token generation
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "jwt-secret")

@pytest.fixture
def app():
    app = create_app()
    app.config.from_object(PytestConfig)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app): # Creates a test client to simulate API requests, like Postman.
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        user = User(email="test@example.com", username="testuser")
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=str(user.id))
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
    }
    return headers