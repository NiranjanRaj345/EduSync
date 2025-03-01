import os
from flask import send_from_directory, current_app, jsonify
from app.main import bp
from datetime import datetime

@bp.route('/')
def index():
    """Landing page."""
    return render_template('main/index.html')

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/health')
def health_check():
    """
    Health check endpoint for Koyeb monitoring.
    
    Returns:
        JSON response with system health status:
            - status: Overall system status
            - timestamp: Current UTC time
            - google_drive: Google Drive integration status
            - database: Database connection status
            - upload_folder: File storage availability
            - storage_paths: Status of required directories
    """
    try:
        upload_base = current_app.config['UPLOAD_FOLDER']
        storage_paths = {
            'uploads': os.path.exists(upload_base),
            'temp': os.path.exists(os.path.join(upload_base, 'temp')),
            'reviews': os.path.exists(os.path.join(upload_base, 'reviews')),
            'student': os.path.exists(os.path.join(upload_base, 'student'))
        }

        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'google_drive': {
                'enabled': current_app.config['USE_GOOGLE_DRIVE'],
                'credentials': bool(os.getenv('GOOGLE_DRIVE_CREDENTIALS_B64')),
                'folder_id': bool(os.getenv('GOOGLE_DRIVE_FOLDER_ID'))
            },
            'database': check_db_connection(),
            'upload_folder': os.path.exists(upload_base),
            'storage_paths': storage_paths
        }

        # Set overall status based on checks
        if not all([health_data['database'], health_data['upload_folder'], 
                   all(storage_paths.values())]):
            health_data['status'] = 'unhealthy'

        status_code = 200 if health_data['status'] == 'healthy' else 503
        return jsonify(health_data), status_code
    except Exception as e:
        error_data = {
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }
        return jsonify(error_data), 500

def check_db_connection() -> bool:
    """
    Verify database connectivity.

    Returns:
        bool: True if database connection is successful, False otherwise
    """
    from app import db
    try:
        # Execute simple query to test connection
        db.session.execute('SELECT 1')
        db.session.commit()  # Ensure transaction is closed
        return True
    except Exception as e:
        current_app.logger.error(f"Database connection error: {str(e)}")
        return False
    finally:
        db.session.close()  # Always close the session

def render_template(*args, **kwargs):
    """Wrapper around flask.render_template."""
    from flask import render_template as flask_render_template
    return flask_render_template(*args, **kwargs)
