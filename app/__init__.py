from flask import Flask, jsonify, request, flash, redirect, url_for
from flask_wtf.csrf import CSRFProtect
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

# Initialize Flask extensions
csrf = CSRFProtect()
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
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window"
)

def create_app(config_name=None):
    if config_name is None:
        config_name = 'production' if os.getenv('FLASK_ENV') == 'production' else 'default'
    app = Flask(__name__)

    # Session and Cookie Security Configuration
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600,  # 1 hour
        REMEMBER_COOKIE_SECURE=True,
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_DURATION=2592000  # 30 days
    )

    # Initialize CSRF protection
    csrf.init_app(app)

    # CSRF Error Handler
    @app.errorhandler(CSRFProtect.error_handler)
    def handle_csrf_error(e):
        app.logger.warning(f"CSRF Error: {str(e)}")
        return redirect(url_for('auth.login')), 302

    # Generic Error Handlers
    @app.errorhandler(400)
    def bad_request_error(e):
        app.logger.warning(f"Bad Request: {str(e)}")
        if request.is_xhr:
            return jsonify({"error": str(e)}), 400
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for('auth.login'))

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Server Error: {str(e)}")
        if request.is_xhr:
            return jsonify({"error": "Internal server error"}), 500
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('main.index'))
    
    # Load config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
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
    
    # Initialize request logger
    from app.utils import init_request_logger
    init_request_logger(app)

    return app
