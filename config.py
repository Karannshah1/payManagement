import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RECEIPTS_DIR = os.path.join(DATA_DIR, 'receipts')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RECEIPTS_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'paymanagement-secret-key-change-in-production')

    # Supabase / PostgreSQL database URL support
    # Render, Heroku and Supabase provide postgres:// which SQLAlchemy 2.0 requires as postgresql://
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or f"sqlite:///{os.path.join(DATA_DIR, 'expenses.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase Configuration (read strictly from environment)
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_PUBLISHABLE_KEY = os.environ.get('SUPABASE_PUBLISHABLE_KEY')
    SUPABASE_SECRET_KEY = os.environ.get('SUPABASE_SECRET_KEY')
    SUPABASE_JWKS_URL = os.environ.get('SUPABASE_JWKS_URL')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = RECEIPTS_DIR
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    ALLOWED_DOC_EXTENSIONS = {'pdf', 'csv', 'xlsx', 'xls', 'zip'}
    DEFAULT_CURRENCY = '₹'
    DEFAULT_CURRENCY_CODE = 'INR'
    ITEMS_PER_PAGE = 25
