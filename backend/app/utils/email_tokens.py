from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_email_confirmation_token(email):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt="email-confirm-salt")

def confirm_email_token(token, expiration=86400):  # 24 hours
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt="email-confirm-salt", max_age=expiration)
    except Exception:
        return None
    return email