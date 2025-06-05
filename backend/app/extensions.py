# Extensions is where all the objects are made. __init__ will initialize them for use.

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS     # Cors allows for frontend and backend frameworks to communicate through different localhost ports.
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
login_manager = LoginManager()
cors = CORS()
jwt = JWTManager()
jwt_blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload): # runs in the background, does not need to be called.
    return jwt_payload["jti"] in jwt_blacklist