from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

from app.models import User
from app.extensions import db, jwt_blacklist
from app.utils.password_tokens import generate_reset_token
from app.utils.email_tokens import generate_email_confirmation_token
from flask_jwt_extended import create_access_token, create_refresh_token


def test_register(client):
    data = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "secret"
    }
    res = client.post("/api/auth/register", json=data)
    assert res.status_code == 201


def test_verify_email(app, client):
    with app.app_context():
        user = User(email="verify@example.com", username="verify", password_hash="x")
        db.session.add(user)
        db.session.commit()
        token = generate_email_confirmation_token(user.email)

    res = client.post(f"/api/auth/verify-email?token={token}")
    assert res.status_code == 200


def test_login(app, client):
    with app.app_context():
        pw = generate_password_hash("pass")
        user = User(email="login@example.com", username="login", password_hash=pw, is_email_confirmed=True)
        db.session.add(user)
        db.session.commit()

    res = client.post("/api/auth/login", json={"email": "login@example.com", "password": "pass"})
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_token_refresh(app, client):
    with app.app_context():
        user = User(email="refresh@example.com", username="refresh", is_email_confirmed=True)
        db.session.add(user)
        db.session.commit()
        refresh = create_refresh_token(identity=str(user.id))

    res = client.post("/api/auth/token/refresh", headers={"Authorization": f"Bearer {refresh}"})
    assert res.status_code == 200


def test_logout(app, client):
    with app.app_context():
        user = User(email="logout@example.com", username="logout", is_email_confirmed=True)
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))

    res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(jwt_blacklist) == 1


def test_forgot_and_reset_password(app, client):
    with app.app_context():
        pw = generate_password_hash("old")
        user = User(email="reset@example.com", username="reset", password_hash=pw)
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user.email)

    res = client.post("/api/auth/forgot-password", json={"email": "reset@example.com"})
    assert res.status_code == 200

    res = client.post("/api/auth/reset-password", json={"token": token, "new_password": "new"})
    assert res.status_code == 200


def test_change_email(app, client):
    with app.app_context():
        pw = generate_password_hash("secret")
        user = User(email="change@example.com", username="change", password_hash=pw, is_email_confirmed=True)
        db.session.add(user)
        db.session.commit()
        access = create_access_token(identity=str(user.id))

    res = client.patch(
        "/api/auth/change-email",
        json={"new_email": "changed@example.com", "password": "secret"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert res.status_code == 200


def test_set_backup_email(app, client):
    with app.app_context():
        pw = generate_password_hash("pw")
        user = User(email="backup@example.com", username="backup", password_hash=pw, is_email_confirmed=True)
        db.session.add(user)
        db.session.commit()
        access = create_access_token(identity=str(user.id))

    res = client.patch(
        "/api/auth/set-backup-email",
        json={"backup_email": "other@example.com"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert res.status_code == 200