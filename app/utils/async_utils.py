import asyncio
from functools import wraps
from asgiref.sync import async_to_sync
from flask import current_app

def async_route(f):
    """Decorator to make async route handlers work with Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # Get the event loop for the current context
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If there's no event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            # Run the async function in the event loop
            return loop.run_until_complete(f(*args, **kwargs))
        except Exception as e:
            current_app.logger.error(f"Error in async route: {str(e)}")
            raise
    return wrapper
