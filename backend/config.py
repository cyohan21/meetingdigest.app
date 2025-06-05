from dotenv import load_dotenv
import os
load_dotenv()

class Config: # So other classes can inherit keys 
    SECRET_KEY = os.getenv("SECRET_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class PytestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory DB for fast unit tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False