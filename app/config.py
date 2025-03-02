import os
import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler

class Config:
    # Flask and Session Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Session Config with Redis primary, filesystem fallback
    SESSION_TYPE = 'redis'  # Default to Redis
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'edusync:'
    
    @classmethod
    def init_redis(cls):
        """Initialize Redis connection with Redis Cloud support"""
        import redis
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print("No Redis URL configured")
            return None
        
        try:
            # Redis Cloud specific configuration
            client = redis.from_url(
                redis_url,
                socket_timeout=10,
                socket_connect_timeout=10,
                socket_keepalive=True,
                retry_on_timeout=True,
                retry_on_error=[redis.exceptions.ConnectionError],
                retry=3,
                ssl=True,
                ssl_cert_reqs='none',  # Required for Redis Cloud
                decode_responses=True
            )
            # Test connection
            client.ping()
            print("Redis Cloud connection successful")
            return client
        except Exception as e:
            print(f"Redis connection error: {str(e)}")  # Debug print
            return None

    # Session configuration
    SESSION_TYPE = 'redis'
    SESSION_KEY_PREFIX = 'edusync:'
    SESSION_USE_SIGNER = True
    SESSION_REDIS = init_redis
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Fallback configuration (will be used if Redis fails)
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flask_session')
    SESSION_FILE_THRESHOLD = 500
    
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
    
    # Database Connection Settings for Neon
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),  # Reduced pool size for Neon
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),  # Recycle every 30 minutes
        'pool_pre_ping': True,  # Enable connection health checks
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '2')),  # Limited overflow for Neon
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'edusync',  # Identify app in Neon logs
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'sslmode': 'verify-full',  # Stricter SSL for Neon
            'options': '-c statement_timeout=30000'  # 30 second timeout
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
    
    # Production database settings optimized for Neon
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),  # Conservative pool size
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
        'pool_pre_ping': True,
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '2')),
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'edusync_production',
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'sslmode': 'verify-full',
            'options': '-c statement_timeout=30000'
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
