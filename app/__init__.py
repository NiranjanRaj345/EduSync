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
from dotenv import load_dotenv
from app.config import config
import os

# Load environment variables
load_dotenv()

# Initialize Flask extensions with optimized connection pooling
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
    
    # Load config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app and configure database retry
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
