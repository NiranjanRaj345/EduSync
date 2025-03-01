from flask import session
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def cleanup_expired_sessions():
    """Clean up expired sessions from Redis"""
    try:
        from flask import current_app
        import redis
        
        # Get Redis client from URL
        redis_url = current_app.config.get('SESSION_REDIS')
        if isinstance(redis_url, str):
            redis_client = redis.from_url(redis_url)
        else:
            redis_client = redis_url
            
        session_prefix = current_app.config.get('SESSION_KEY_PREFIX', 'session:')
        
        # Get all session keys
        session_pattern = f"{session_prefix}*"
        session_keys = redis_client.keys(session_pattern)
        
        # Check each session
        for key in session_keys:
            session_data = redis_client.get(key)
            if not session_data:
                continue
                
            try:
                import json
                session_dict = json.loads(session_data)
                login_time = session_dict.get('login_time')
                
                if login_time:
                    login_datetime = datetime.fromisoformat(login_time)
                    session_lifetime = current_app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=24))
                    
                    # Remove expired sessions
                    if datetime.utcnow() - login_datetime > session_lifetime:
                        redis_client.delete(key)
                        logger.info(f"Cleaned up expired session: {key}")
            except Exception as e:
                logger.error(f"Error processing session {key}: {str(e)}")
                continue
                    
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
