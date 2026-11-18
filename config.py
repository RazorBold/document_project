import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE = os.path.join(basedir, os.getenv('DB_PATH', 'monitoring.db'))
    ON_VERCEL = bool(os.getenv('VERCEL'))
    # On Vercel there is no persistent server, so Socket.IO runs in 'threading' mode
    # only to keep server-side emit() calls harmless; the browser client is disabled.
    SOCKETIO_ASYNC_MODE = 'threading' if ON_VERCEL else os.getenv('SOCKETIO_ASYNC_MODE', 'eventlet')
    REALTIME_ENABLED = (not ON_VERCEL) and os.getenv('REALTIME_ENABLED', '1') == '1'
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = '/tmp/uploads' if ON_VERCEL else os.path.join(basedir, 'static', 'uploads')
    # Supabase Storage for attachments (optional; used when both are set)
    SUPABASE_URL = os.getenv('SUPABASE_URL', '').rstrip('/')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
    SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'uploads')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
