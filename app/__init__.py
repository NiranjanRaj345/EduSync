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
    
    # Initialize Redis and Session
    try:
        # Get Redis client
        if callable(app.config['SESSION_REDIS']):
            redis_client = app.config['SESSION_REDIS']()
        else:
            redis_client = app.config['SESSION_REDIS']
            
        # Test Redis connection
        if isinstance(redis_client, redis.Redis):
            redis_client.ping()
            app.logger.info("Redis connection established successfully")
        else:
            raise Exception("Invalid Redis client configuration")
            
    except Exception as e:
        app.logger.error(f"Redis initialization failed: {str(e)}")
        raise RuntimeError(f"Could not initialize Redis: {str(e)}")
    
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
    
    # Initialize session after Redis is confirmed working
    try:
        sess.init_app(app)
        app.logger.info("Flask-Session initialized successfully")
    except Exception as e:
        app.logger.error(f"Session initialization failed: {str(e)}")
        raise RuntimeError(f"Could not initialize sessions: {str(e)}")
    
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
