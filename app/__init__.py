from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from dotenv import load_dotenv
from app.config import config
import redis
import os
import time

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy(engine_options={
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'pool_timeout': 30,
})
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
sess = Session()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window"
)

def create_app(config_name=None):
    if config_name is None:
        config_name = 'production' if os.getenv('FLASK_ENV') == 'production' else 'default'
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize Redis and Session with retries
    max_retries = 3
    retry_delay = 2  # seconds
    
    try:
        for attempt in range(max_retries):
            app.logger.info(f"Redis connection attempt {attempt + 1}/{max_retries}")
            
            if app.config['SESSION_TYPE'] == 'redis':
                try:
                    redis_client = None
                    if callable(app.config['SESSION_REDIS']):
                        app.logger.info("Initializing Redis Cloud client")
                        redis_client = app.config['SESSION_REDIS']()
                        
                        if redis_client:
                            # Test connection with retry
                            retry_count = 0
                            while retry_count < 3:
                                try:
                                    redis_client.ping()
                                    app.logger.info("Redis Cloud connection established")
                                    break
                                except Exception as e:
                                    retry_count += 1
                                    if retry_count == 3:
                                        raise
                                    app.logger.warning(f"Redis ping attempt {retry_count} failed, retrying...")
                                    time.sleep(1)
                        else:
                            raise Exception("Redis client initialization returned None")
                except Exception as e:
                    app.logger.error(f"Redis Cloud initialization failed: {str(e)}")
                    if attempt == max_retries - 1:
                        app.logger.info("Falling back to filesystem sessions after all retries")
                        app.config['SESSION_TYPE'] = 'filesystem'
                        os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
                    else:
                        time.sleep(retry_delay)
                        continue
            
            # Initialize Session with chosen backend
            sess.init_app(app)
            app.logger.info(f"Session initialized with {app.config['SESSION_TYPE']} backend")
            break  # Successfully initialized, break the retry loop
            
    except Exception as e:
        app.logger.error(f"Session initialization failed: {str(e)}")
        raise RuntimeError(f"Could not initialize sessions: {str(e)}")
    
    # Initialize extensions with app and configure database retry
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    }
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.student import bp as student_bp
    from app.faculty import bp as faculty_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)
    
    return app
