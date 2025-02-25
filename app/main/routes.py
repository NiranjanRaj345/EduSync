import os
from flask import render_template, current_app, send_from_directory, redirect, url_for
from flask_login import current_user
from app.main import bp
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Check if the file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        else:
            return redirect(url_for('faculty.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(
        os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER']),
        filename
    )

def save_file(file, directory=''):
    """Save uploaded file and return the secure filename"""
    filename = secure_filename(file.filename)
    # Create unique filename to prevent overwrites
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(
        current_app.root_path,
        current_app.config['UPLOAD_FOLDER'],
        directory,
        filename
    )):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    
    # Create directory if it doesn't exist
    full_path = os.path.join(
        current_app.root_path,
        current_app.config['UPLOAD_FOLDER'],
        directory
    )
    os.makedirs(full_path, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(full_path, filename)
    file.save(file_path)
    
    return filename
