from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app.auth import check_active_session
from app import db, limiter
from app.student import bp
from app.models import Document, User
from app.config import Config
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        logger.warning(f"Attempted upload of file with unauthorized extension: {ext}")
        return False
    return True

def save_file(file, directory):
    """Save file with secure filename in specified directory"""
    filename = secure_filename(file.filename)
    # Add timestamp to filename to prevent overwriting
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{name}_{timestamp}{ext}"
    
    upload_path = current_app.config['UPLOAD_FOLDER']
    if not os.path.isabs(upload_path):
        upload_path = os.path.abspath(upload_path)
    path = os.path.join(upload_path, directory)
    os.makedirs(path, exist_ok=True)
    
    try:
        file_path = os.path.join(path, filename)
        os.makedirs(path, exist_ok=True)  # Ensure directory exists
        file.save(file_path)
        logger.info(f"File saved successfully at: {file_path}")
        return filename
    except Exception as e:
        logger.error(f"Error saving file {filename}: {str(e)}")
        raise

@bp.route('/student/dashboard')
@login_required
@check_active_session
def dashboard():
    if current_user.role != 'student':
        logger.warning(f"Non-student user {current_user.id} attempted to access student dashboard")
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.index'))
    
    documents = Document.query.filter_by(uploader_id=current_user.id).order_by(
        Document.upload_date.desc()
    ).all()
    return render_template('student/dashboard.html', documents=documents)

@bp.route('/student/upload_document', methods=['GET', 'POST'])
@login_required
@check_active_session
@limiter.limit(Config.UPLOAD_RATELIMIT)
def upload_document():
    if current_user.role != 'student':
        logger.warning(f"Non-student user {current_user.id} attempted to upload document")
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.index'))

    # Get list of faculty members for dropdown
    faculties = User.query.filter_by(role='faculty').order_by(User.first_name).all()
    
    if request.method == 'POST':
        # Validate faculty selection
        faculty_id = request.form.get('faculty')
        if not faculty_id:
            flash('Please select a faculty member', 'danger')
            return redirect(request.url)
            
        faculty = User.query.filter_by(id=faculty_id, role='faculty').first()
        if not faculty:
            flash('Invalid faculty selection', 'danger')
            return redirect(request.url)
        if 'document' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['document']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('File type not allowed. Allowed types: ' + 
                  ', '.join(current_app.config['ALLOWED_EXTENSIONS']), 'danger')
            return redirect(request.url)
        
        try:
            # Save file with student's ID in the path
            directory = f"student_{current_user.id}"
            filename = save_file(file, directory)
            
            # Create document record
            document = Document(
                filename=filename,
                original_filename=secure_filename(file.filename),
                file_path=os.path.join(directory, filename),
                file_type=file.filename.rsplit('.', 1)[1].lower(),
                uploader_id=current_user.id,
                assigned_faculty_id=faculty.id
            )
            
            db.session.add(document)
            db.session.commit()
            
            logger.info(f"Document {filename} uploaded successfully by user {current_user.id}")
            flash('Document uploaded successfully', 'success')
            return redirect(url_for('student.dashboard'))
            
        except Exception as e:
            logger.error(f"Error in document upload: {str(e)}")
            flash(f'Error uploading document: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('student/upload.html', faculties=faculties)

@bp.route('/student/document/<int:id>')
@login_required
@check_active_session
def view_document(id):
    if current_user.role != 'student':
        logger.warning(f"Non-student user {current_user.id} attempted to view document {id}")
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.index'))
    
    document = Document.query.get_or_404(id)
    
    # Ensure student can only view their own documents
    if document.uploader_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to access document {id} owned by user {document.uploader_id}")
        flash('Access denied. You can only view your own documents.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    return render_template('student/document.html', document=document)
