import logging
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from datetime import timedelta
import asyncio
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from app.config import config
import os

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy(engine_options={
    'pool_size': 20,            # Increased for more concurrent users
    'pool_recycle': 900,        # Reduced to 15 minutes for better recycling
    'pool_pre_ping': True,      # Keep enabled for connection health checks
    'pool_timeout': 60,         # Increased for better timeout handling
    'max_overflow': 10,         # Allow more overflow connections
    'pool_use_lifo': True,      # Use LIFO for better performance
})
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window"
)

def create_app(config_name=None):
    if config_name is None:
        config_name = 'production' if os.getenv('FLASK_ENV') == 'production' else 'default'
    app = Flask(__name__)
    
    # Configure logging
    if os.getenv('FLASK_ENV') != 'production':
        app.debug = True
        logging.basicConfig(level=logging.DEBUG)
        # Enable Redis debug logging
        logging.getLogger('app.utils.redis_client').setLevel(logging.DEBUG)
    else:
        app.debug = False
        logging.basicConfig(level=logging.INFO)
    
    # Load config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configure base session settings
    app.config.update(
        SESSION_COOKIE_NAME='edusync_session',
        SESSION_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=1)
    )
    
    # Configure secret key if not set
    if not app.secret_key:
        app.secret_key = os.urandom(32)
    
    # Initialize extensions with app
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '20')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '900')),
        'pool_pre_ping': True,
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '60')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),
        'pool_use_lifo': True,
        'connect_args': {
            'connect_timeout': 20,
            'keepalives': 1,
            'keepalives_idle': 60,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    }
    
    # Initialize core extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # Setup event loop for async operations
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Initialize Redis and session handling
    if app.config.get('UPSTASH_REDIS_REST_URL') and app.config.get('UPSTASH_REDIS_REST_TOKEN'):
        from app.utils.redis_client import RedisManager
        from app.utils.session_interface import UpstashRedisSessionInterface
        redis_manager = RedisManager()
        try:
            redis_manager.init_app(app)
            # Make redis_manager available to the app
            app.redis = redis_manager
            # Use custom session interface with proper app context
            session_interface = UpstashRedisSessionInterface(
                redis=redis_manager,  # Pass manager instead of client
                app=app,
                use_signer=True,
                permanent=True
            )
            app.session_interface = session_interface
            app.logger.info("Redis session interface initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize Redis: {str(e)}")
            app.logger.warning("Falling back to default session interface")
    else:
        app.logger.warning("Redis configuration not found, using default session interface")
    
    # Configure login manager with secure settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'Please login again to confirm your identity'
    login_manager.needs_refresh_message_category = 'info'
    login_manager.session_protection = 'strong'
    
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
