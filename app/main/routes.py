from flask import send_from_directory, current_app, abort, redirect, url_for
import logging

logger = logging.getLogger(__name__)
from flask_login import login_required, current_user
from app.main import bp
from app.models import Document
import os

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        else:
            return redirect(url_for('faculty.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    # Security check - verify if user has access to the file
    if filename.startswith('reviews/'):
        # For review files, check if user is faculty or the student who owns the reviewed document
        doc_id = filename.split('/')[1].split('_')[1]
        document = Document.query.get(doc_id)
        if not document:
            abort(404)
        if current_user.role == 'faculty' and document.assigned_faculty_id != current_user.id:
            abort(403)
        elif current_user.role == 'student' and document.uploader_id != current_user.id:
            abort(403)
    else:
        # For student uploads, check if user owns the file or is assigned faculty
        student_id = filename.split('/')[0].split('_')[1]
        if current_user.role == 'student' and str(current_user.id) != student_id:
            abort(403)
        elif current_user.role == 'faculty':
            document = Document.query.filter_by(file_path=filename).first()
            if not document or document.assigned_faculty_id != current_user.id:
                abort(403)

    try:
        upload_path = current_app.config['UPLOAD_FOLDER']
        if not os.path.isabs(upload_path):
            upload_path = os.path.abspath(upload_path)
        
        file_path = os.path.join(upload_path, filename)
        directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        
        return send_from_directory(directory, file_name)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        abort(404)
