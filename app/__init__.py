import os
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
sess = Session()

def create_app(config_class: Optional[object] = None) -> Flask:
    """
    Creates and configures the Flask application.
    
    Args:
        config_class: Optional configuration class to use instead of default Config
    
    Returns:
        Flask: The configured Flask application instance
        
    Raises:
        ImportError: If blueprint modules cannot be imported
        Exception: For other initialization errors
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        # Default to Config from app.config
        from app.config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    # Ensure upload directories exist
    upload_paths = {
        'base': app.config['UPLOAD_FOLDER'],
        'temp': 'temp',
        'reviews': 'reviews',
        'student': 'student'
    }
    
    try:
        # Create upload directories
        for path_type, subdir in upload_paths.items():
            if path_type == 'base':
                directory = os.path.join(app.root_path, subdir)
            else:
                directory = os.path.join(app.root_path, upload_paths['base'], subdir)
            os.makedirs(directory, exist_ok=True)
            if not app.debug:  # Only log in production
                app.logger.info(f"Created directory: {directory}")
    except Exception as e:
        app.logger.error(f"Error creating directories: {str(e)}")
        raise

    # Initialize Flask extensions with error handling
    extensions = [
        (db, 'SQLAlchemy'),
        (migrate, 'Migrate', [app, db]),
        (login, 'Login'),
        (mail, 'Mail'),
        (limiter, 'Rate Limiter'),
        (sess, 'Session')
    ]
    
    for ext, name, *args in extensions:
        try:
            if args:
                ext.init_app(*args)
            else:
                ext.init_app(app)
            if not app.debug:
                app.logger.info(f"Initialized {name} extension")
        except Exception as e:
            app.logger.error(f"Error initializing {name}: {str(e)}")
            raise
    
    # Set up logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure file logging
        log_file = os.path.join(log_dir, 'edusync.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Set up logging level
        app.logger.setLevel(logging.INFO)
        app.logger.info('Document System startup')
        
        # Log configuration status
        app.logger.info('Google Drive: %s', 'enabled' if app.config['USE_GOOGLE_DRIVE'] else 'disabled')
        app.logger.info('Database: PostgreSQL with connection pooling')
        app.logger.info('Upload path: %s', os.path.abspath(app.config['UPLOAD_FOLDER']))
        
    # Register blueprints with better error handling
    blueprints = {
        'main': ('app.main', 'bp'),
        'auth': ('app.auth', 'bp'),
        'student': ('app.student', 'bp'),
        'faculty': ('app.faculty', 'bp')
    }
    
    for name, (module_path, attr) in blueprints.items():
        try:
            module = __import__(module_path, fromlist=[attr])
            blueprint = getattr(module, attr)
            app.register_blueprint(blueprint)
            if not app.debug:
                app.logger.info(f"Registered blueprint: {name} from {module_path}")
        except ImportError as e:
            app.logger.error(f"Failed to import blueprint {name} from {module_path}: {str(e)}")
            raise
        except Exception as e:
            app.logger.error(f"Failed to register blueprint {name}: {str(e)}")
            raise

    return app

# Import models to register them with SQLAlchemy
from app import models
