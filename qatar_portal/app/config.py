import os
from dotenv import load_dotenv
load_dotenv()

class DevelopmentConfig:
    SECRET_KEY                     = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI        = os.environ.get("DATABASE_URL", "sqlite:///qatar_portal.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE                   = "filesystem"
    SESSION_PERMANENT              = False
    SESSION_FILE_DIR               = "./flask_session"
    DEBUG                          = True

class ProductionConfig:
    SECRET_KEY                     = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI        = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE                   = "filesystem"
    SESSION_PERMANENT              = False
    SESSION_COOKIE_SECURE          = True
    SESSION_COOKIE_HTTPONLY        = True
    SESSION_COOKIE_SAMESITE        = "Lax"
    DEBUG                          = False
