from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
from app.utils.password_tokens import generate_reset_token, confirm_reset_token
from app.utils.email_tokens import generate_email_confirmation_token, confirm_email_token
from app.extensions import db
from app.models import User
from datetime import datetime, timezone
from app.extensions import jwt_blacklist
from flask_cors import cross_origin

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/token/refresh", methods=["POST"], endpoint="token-refresh") # Add endpoints so JWT can differentiate the functions for each route.
@jwt_required(refresh=True) # Refresh=True establishes a refresh token, rather than an access token.
def refresh_token():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": new_access_token}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user.id, "email": user.email})


@auth_bp.route("/register", methods=["POST"], endpoint="register")
def register():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    backup_email = data.get("backup_email")

    if not username or not email or not password:
        return jsonify({"error": "Email, username or password not entered."}), 400
    
    if User.query.filter((User.email==email) | (User.username==username)).first():
        return jsonify({"mesg": "Username or email already registered."}), 409
    
    hashed_pw = generate_password_hash(password)
    new_user = User(
        email=email.lower(),
        username = username,
        password_hash=hashed_pw,
        backup_email=backup_email.lower() if backup_email else None,
        is_email_confirmed=False # for clarity, already set to false in the models.
        )
    
    db.session.add(new_user)
    db.session.commit()

    token = generate_email_confirmation_token(email)
    confirm_link = f"http://localhost:1011/verify-email?token={token}" # for testing, change this to the actual localhost port when frontend initialized.

    print("EMAIL CONFIRMATION LINK:", confirm_link)  # TODO: Send email

    return jsonify({"msg": "Account created. Please confirm your email."}), 201

@auth_bp.route("/verify-email", methods=["POST"], endpoint="verify-email")
def verify_email():
    token = request.args.get("token")
    email = confirm_email_token(token)

    if not email:
        return jsonify({"error": "Invalid or expired token."}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found."}), 400
    
    if user.is_email_confirmed:
        return jsonify({"msg": "Email already confirmed."}), 200
    
    user.is_email_confirmed = True
    db.session.commit()

    return jsonify({"msg": "Email verified successfully."}), 200

@auth_bp.route("/login", methods=["POST"], endpoint="login")
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
def login():
    try:
        data = request.get_json()
        email = data.get("email", "").lower()
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials."}), 401
        
        if not user.is_email_confirmed: # do not need data.get, as that will rely on user input (we don't want that.)
            return jsonify({"error": "Please confirm your email first."}), 403
        
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        response = jsonify({
            "msg": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
            })
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response
    except Exception as e:
        print("[LOGIN ERROR]", e)
        return jsonify({"error": "Server error occurred"}), 500

@auth_bp.route("/logout", methods=["POST"], endpoint="logout")
@jwt_required()
def logout():
    # Revoke access token
    access_jti = get_jwt()["jti"] # Extract JWT ID from access token
    jwt_blacklist.add(access_jti)

    # Try to revoke refresh token
    try:
        verify_jwt_in_request(refresh=True, locations=["headers", "cookies"], header_name="X-Refresh-Token") # Finding it either in headers (postman) or cookies (websites).
        refresh_jti = get_jwt()["jti"]
        jwt_blacklist.add(refresh_jti)
    except Exception as e:
        print("[LOGOUT] Refresh token not provided or invalid.")

    response = jsonify({"msg": "Logged out"})
    unset_jwt_cookies(response)
    return response


@auth_bp.route("/forgot-password", methods=["POST"], endpoint="forgot-password")
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter(
        (User.email == email) | (User.backup_email == email)
    ).first()
    
    if not user:
        return jsonify({"error": "No user found."}), 400
    
    token = generate_reset_token(user.email)
    reset_link = f"http://localhost:1011/api/auth/reset-password?token={token}" # change this after the frontend is established.

    print("Reset link:", reset_link) # Send this via email when in production.

    return jsonify({"msg": "Password reset link sent."}), 200

@auth_bp.route("/reset-password", methods=["POST"], endpoint="reset-password")
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    email = confirm_reset_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired token."}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"msg": "Password reset successful."}), 200


@auth_bp.route("/change-email", methods=["PATCH"], endpoint="change-email")
@jwt_required()
def change_email():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    new_email = data.get("new_email").lower()
    current_password = data.get("password")

    if not new_email or not current_password:
        return jsonify({"error": "New email and password are required."}), 400

    if new_email == user.backup_email:
        return jsonify({"error": "Email entered is already your backup email."}), 400
    
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"error": "Password Incorrect."}), 400
    
    if User.query.filter((User.email==new_email) | (User.backup_email==new_email)).first():
        return jsonify({"error": "Email already in use."}), 400
    
    user.email = new_email
    db.session.commit()

    return jsonify({"msg": "Email successfully changed."}), 200

@auth_bp.route("/set-backup-email", methods=["PATCH"], endpoint="set-backup-email")
@jwt_required()
def set_backup_email():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    backup_email = data.get("backup_email")

    if not backup_email:
        return jsonify({"error": "Backup email is required."}), 400
    
    if backup_email == user.email:
        return jsonify({"error": "Backup email cannot also be your current email."}), 400
    
    if backup_email == user.backup_email:
        return jsonify({"error": "This is already your backup email."}), 400
    
    if User.query.filter((User.email==backup_email) | (User.backup_email==backup_email)).first():
        return jsonify({"error": "Email already in use."}), 400
    
    user.backup_email = backup_email
    db.session.commit()

    return jsonify({"msg": "Backup email successfully set."}), 200

