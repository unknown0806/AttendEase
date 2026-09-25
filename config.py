import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'attendx-secret-key-hackathon-2026')
    
    # Database config: supports direct DATABASE_URL or component variables, with SQLite fallback
    database_url = os.getenv('DATABASE_URL')
    
    # Normalize postgres:// to postgresql:// for SQLAlchemy compatibility (e.g. Supabase, Neon, Heroku)
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    if not database_url:
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_name = os.getenv('DB_NAME', 'attendx')
        
        if db_user and db_password:
            database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
        else:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            bundled_db = os.path.join(base_dir, 'attendx.db')
            
            # Detect serverless environment (Vercel / AWS Lambda) where root directory is read-only
            is_serverless = bool(
                os.getenv('VERCEL') or 
                os.getenv('VERCEL_ENV') or 
                os.getenv('AWS_LAMBDA_FUNCTION_NAME')
            )
            
            if is_serverless:
                import shutil
                tmp_db = '/tmp/attendx.db'
                if not os.path.exists(tmp_db) and os.path.exists(bundled_db):
                    try:
                        shutil.copyfile(bundled_db, tmp_db)
                    except Exception as e:
                        print(f"Notice: Failed to copy bundled DB to /tmp: {e}")
                database_url = f"sqlite:///{tmp_db}"
            else:
                database_url = f"sqlite:///{bundled_db}"
            
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
