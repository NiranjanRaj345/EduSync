import os
import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from redis import Redis
from app.utils.session import RedisSessionInterface

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    
    # Session Configuration
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_KEY_PREFIX = 'session:'
    SESSION_COOKIE_NAME = 'edusync_session'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @staticmethod
    def init_redis():
        return Redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            socket_timeout=3
        )
    
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
    
    # Database Connection Settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
        'pool_pre_ping': True,
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '5')),
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'sslmode': 'require'
        }
    }
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '20971520'))
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'txt', 'zip',
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
    UPLOAD_RATELIMIT = "10/hour"
    
    @staticmethod
    def init_app(app):
        # Redis session interface
        redis_client = Config.init_redis()
        app.session_interface = RedisSessionInterface(
            redis=redis_client,
            prefix=app.config.get('SESSION_KEY_PREFIX', 'session:')
        )
        
        # Ensure upload directory exists
        os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
        
        # Configure logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
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
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        app.logger.addHandler(console_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Document System startup')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_DOMAIN = '.koyeb.app'
    SESSION_COOKIE_SECURE = True
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': int(os.getenv('DB_POOL_SIZE', '20')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),
        'connect_args': {
            **Config.SQLALCHEMY_ENGINE_OPTIONS['connect_args'],
            'application_name': 'edusync_production',
        }
    }
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        db_logger = logging.getLogger('sqlalchemy.engine')
        db_logger.setLevel(logging.WARNING)
        
        def handle_db_error(exception):
            app.logger.error(f"Database Error: {str(exception)}")
            
        app.logger.info("Production database configuration initialized")
        
        from logging.handlers import SMTPHandler
        credentials = None
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_USERNAME'],
            toaddrs=['admin@yourdomain.com'],
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
