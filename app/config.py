import os
import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Redis Configuration
    UPSTASH_REDIS_REST_URL = os.getenv('UPSTASH_REDIS_REST_URL')
    UPSTASH_REDIS_REST_TOKEN = os.getenv('UPSTASH_REDIS_REST_TOKEN')
    
    # Session Configuration
    SESSION_TYPE = 'redis'
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('SESSION_LIFETIME', '86400')))  # 24 hours
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_VALIDATION_ENABLED = True
    SESSION_REFRESH_EACH_REQUEST = True
    
    # Database
    @staticmethod
    def get_database_url():
        """Get database URL with proper error handling and retry mechanism"""
        url = os.getenv('DATABASE_URL', 'postgresql://uploadmanager:uploadmanager0.0.1.1@localhost:5432/document_system')
        if url.startswith('postgres://'):  # Handle Neon's connection string format
            url = url.replace('postgres://', 'postgresql://', 1)
        return url

    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database Connection Settings for Neon (Optimized for concurrent users)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '20')),      # Increased pool size
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '900')), # 15 minute recycle
        'pool_pre_ping': True,                                   # Health checks
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '60')), # Increased timeout
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')), # More overflow connections
        'pool_use_lifo': True,                                   # LIFO for better performance
        'connect_args': {
            'connect_timeout': 20,                               # Increased timeout
            'application_name': 'edusync',                       # App identifier
            'keepalives': 1,
            'keepalives_idle': 60,                              # Increased idle time
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'sslmode': 'verify-full',                           # SSL security
            'options': '-c statement_timeout=60000'             # 60 second timeout
        }
    }
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app/uploads'))
    # 20MB max file size
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '20971520'))
    ALLOWED_EXTENSIONS = {
        'pdf',  # Documents
        'doc', 'docx',  # Microsoft Word
        'txt',  # Text files
        'zip',  # Archives
    }
    
    # Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_STRATEGY = "fixed-window"
    
    # File Upload Rate Limits
    UPLOAD_RATELIMIT = "10/hour"  # Limit file uploads
    
    @staticmethod
    def init_app(app):
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Configure logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        # File Handler - Detailed logging
        file_handler = RotatingFileHandler(
            'logs/document_system.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Console Handler - Error level only
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        app.logger.addHandler(console_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Document System startup')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    # Session and cookie settings for production
    SESSION_COOKIE_NAME = '__Host-session'  # More secure session cookie
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    
    # Production database settings optimized for concurrency
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '20')),      # Increased pool
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '900')), # Faster recycling
        'pool_pre_ping': True,
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '60')), # Longer timeout
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')), # More overflow
        'pool_use_lifo': True,                                   # Better performance
        'connect_args': {
            'connect_timeout': 20,
            'application_name': 'edusync_production',
            'keepalives': 1,
            'keepalives_idle': 60,                              # Longer idle time
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'sslmode': 'verify-full',
            'options': '-c statement_timeout=60000'             # Longer timeout
        }
    }
    
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configure database logging
        db_logger = logging.getLogger('sqlalchemy.engine')
        db_logger.setLevel(logging.WARNING)
        
        # Log database disconnections
        def handle_db_error(exception):
            app.logger.error(f"Database Error: {str(exception)}")
            
        app.logger.info("Production database configuration initialized")
        
        # Email errors to admins
        from logging.handlers import SMTPHandler
        credentials = None
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_USERNAME'],
            toaddrs=['admin@yourdomain.com'],  # Configure admin email
            subject='Document System Failure',
            credentials=credentials,
            secure=() if app.config['MAIL_USE_TLS'] else None
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
        

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
