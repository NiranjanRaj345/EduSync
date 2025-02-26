from flask import request, current_app
from time import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        start_time = time()

        if path.startswith('/auth/login'):
            form_data = {}
            if method == 'POST':
                try:
                    from werkzeug.urls import url_decode
                    content_length = int(environ.get('CONTENT_LENGTH', 0))
                    body = environ['wsgi.input'].read(content_length)
                    form_data = url_decode(body)
                    # Only log email presence, not the actual email
                    if 'email' in form_data:
                        form_data = {'has_email': True}
                except Exception as e:
                    logger.error(f"Error reading form data: {str(e)}")
                    form_data = {'error': 'Could not read form data'}

            logger.info(
                f"Auth Request: {method} {path} "
                f"Query String: {environ.get('QUERY_STRING', '')} "
                f"Form Data: {form_data}"
            )

        def logging_start_response(status, headers, exc_info=None):
            duration = time() - start_time
            logger.info(
                f"Response: {status} "
                f"Duration: {duration:.4f}s "
                f"Path: {path} "
                f"Method: {method}"
            )
            return start_response(status, headers, exc_info)

        return self.app(environ, logging_start_response)

def init_request_logger(app):
    app.wsgi_app = RequestLoggerMiddleware(app.wsgi_app)
