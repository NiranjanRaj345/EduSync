from flask import session
from datetime import datetime, timedelta
from functools import wraps
import logging
import os

logger = logging.getLogger(__name__)

def check_session_expired(session_data):
    """Check if a session has expired"""
    try:
        login_time = session_data.get('login_time')
        if login_time:
            from flask import current_app
            login_datetime = datetime.fromisoformat(login_time)
            session_lifetime = current_app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=24))
            return datetime.utcnow() - login_datetime > session_lifetime
    except Exception as e:
        logger.error(f"Error checking session expiry: {str(e)}")
        return True
    return False

def cleanup_expired_sessions():
    """Clean up expired sessions from storage backend"""
    try:
        from flask import current_app
        
        # Handle different session types
        session_type = current_app.config.get('SESSION_TYPE')
        
        if session_type == 'redis':
            import redis
            import json
            
            # Get Redis client from URL
            redis_url = current_app.config.get('SESSION_REDIS')
            if isinstance(redis_url, str):
                redis_client = redis.from_url(redis_url)
            else:
                redis_client = redis_url
                
            session_prefix = current_app.config.get('SESSION_KEY_PREFIX', 'session:')
            
            # Clean Redis sessions
            try:
                session_pattern = f"{session_prefix}*"
                session_keys = redis_client.keys(session_pattern)
                
                # Process Redis sessions
                for key in session_keys:
                    try:
                        session_data = redis_client.get(key)
                        if session_data:
                            session_dict = json.loads(session_data)
                            if check_session_expired(session_dict):
                                redis_client.delete(key)
                                logger.info(f"Cleaned up expired Redis session: {key}")
                    except Exception as e:
                        logger.error(f"Error processing Redis session {key}: {str(e)}")
                        
            except redis.ConnectionError as e:
                logger.error(f"Redis connection error during cleanup: {str(e)}")
                return
                
        elif session_type == 'filesystem':
            import pickle
            from datetime import datetime
            
            session_dir = current_app.config.get('SESSION_FILE_DIR')
            if not session_dir or not os.path.exists(session_dir):
                return
                
            # Clean filesystem sessions
            for filename in os.listdir(session_dir):
                file_path = os.path.join(session_dir, filename)
                try:
                    with open(file_path, 'rb') as f:
                        session_data = pickle.load(f)
                        if check_session_expired(session_data):
                            os.remove(file_path)
                            logger.info(f"Cleaned up expired filesystem session: {filename}")
                except Exception as e:
                    logger.error(f"Error processing filesystem session {filename}: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Session cleanup error: {str(e)}")

def check_active_session(view_function):
    """Decorator to check if session is still valid"""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        try:
            # Run cleanup periodically (1% chance per request)
            import random
            if random.random() < 0.01:
                cleanup_expired_sessions()
            
            # Check if session exists and is valid
            login_time = session.get('login_time')
            if not login_time:
                return view_function(*args, **kwargs)
            
            # Validate session age
            login_datetime = datetime.fromisoformat(login_time)
            session_lifetime = timedelta(hours=24)  # Default 24 hours
            
            if datetime.utcnow() - login_datetime > session_lifetime:
                session.clear()
                from flask import flash, redirect, url_for
                flash('Your session has expired. Please log in again.', 'info')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            logger.error(f"Session check error: {str(e)}")
            
        return view_function(*args, **kwargs)
    return wrapped_view
