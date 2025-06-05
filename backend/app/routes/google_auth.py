from flask import Blueprint, jsonify, url_for
from ..oauth import oauth
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)
from app.extensions import db
from app.models import User
from datetime import datetime, timezone

google_auth_bp = Blueprint("google_auth", __name__)

@google_auth_bp.route("/login", methods=["GET"])
def google_login():
    redirect_uri = url_for("google_auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@google_auth_bp.route("/callback", methods=["GET"])
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.userinfo()

    email = user_info["email"]
    sub = user_info["sub"]

    user = User.query.filter_by(google_id=sub).first()
    if not user:
        user = User(
            google_id=sub,
            email=email,
            username=email.split("@")[0],
            is_email_confirmed=True
        )
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id
    }), 200