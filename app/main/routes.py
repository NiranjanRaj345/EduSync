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
    """Health check endpoint for Koyeb."""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'google_drive': current_app.config['USE_GOOGLE_DRIVE'],
        'database': check_db_connection(),
        'upload_folder': os.path.exists(current_app.config['UPLOAD_FOLDER'])
    }
    return jsonify(health_data)

def check_db_connection():
    """Check database connection."""
    from app import db
    try:
        db.session.execute('SELECT 1')
        return True
    except Exception:
        return False

def render_template(*args, **kwargs):
    """Wrapper around flask.render_template."""
    from flask import render_template as flask_render_template
    return flask_render_template(*args, **kwargs)
