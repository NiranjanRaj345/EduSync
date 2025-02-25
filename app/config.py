import os
import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    
    # Database
    @staticmethod
    def get_database_url():
        url = os.getenv('DATABASE_URL', 'postgresql://uploadmanager:uploadmanager0.0.1.1@localhost:5432/document_system')
        if url.startswith('postgres://'):  # Handle Neon's connection string format
            url = url.replace('postgres://', 'postgresql://', 1)
        return url

    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
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
        os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
        
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
    SERVER_NAME = os.getenv('SERVER_NAME', 'edusync.koyeb.app')
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_DOMAIN = '.koyeb.app'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
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
        
        # Production security headers
        @app.after_request
        def add_security_headers(response):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            return response

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
