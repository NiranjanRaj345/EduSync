import asyncio
import os
from functools import wraps
from flask import current_app

def async_route(f):
    """Decorator to make async route handlers work with Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # First try to get existing loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Loop is closed")
            except RuntimeError:
                # If there's no loop or it's closed, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async function in the event loop
            with current_app.app_context():
                result = loop.run_until_complete(f(*args, **kwargs))
                
            return result
        
        except Exception as e:
            current_app.logger.error(f"Error in async route: {str(e)}", exc_info=True)
            raise
        
    return wrapper

def setup_async(app=None):
    """Setup async environment based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'production')
    
    try:
        if env == 'production':
            # Use default event loop policy for production
            policy = asyncio.get_event_loop_policy()
            loop = policy.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            # Use uvloop in development if available
            try:
                import uvloop
                uvloop.install()
            except ImportError:
                pass
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except Exception as e:
        if app:
            app.logger.error(f"Error setting up async environment: {str(e)}")
        # Fallback to default event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop
