from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(db.Model): # Add indexing for faster SELECT queries on SQL. Primary keys already allow for indexing.
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    backup_email = db.Column(db.String(120), unique=True, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200)) # not nullable so that OAuth can create users. Nullability for regular users enforced in backend/app/auth.
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
        index=True
        )
    is_email_confirmed = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    filename = db.Column(db.String, nullable=False)
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
        index=True
)
    user = db.relationship("User", backref="records")
