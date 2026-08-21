import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'attendease-secret-key-hackathon-2026')
    
    # Database config: supports direct DATABASE_URL or component variables, with SQLite fallback
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_name = os.getenv('DB_NAME', 'attendease')
        
        if db_user and db_password:
            database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
        else:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            database_url = f"sqlite:///{os.path.join(base_dir, 'attendease.db')}"
            
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
