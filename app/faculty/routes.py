from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db, limiter
from app.faculty import bp
from app.models import Document, User
from app.faculty.utils import send_review_notification
from app.config import Config
from app.utils.file_utils import allowed_file, save_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

@bp.route('/faculty/dashboard')
@limiter.limit("100/hour")
@login_required
def dashboard():
    if current_user.role != 'faculty':
        flash('Access denied. Faculty only.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get documents assigned to this faculty member that are pending review
    documents = Document.query.filter_by(
        assigned_faculty_id=current_user.id,
        status='pending_review'
    ).order_by(Document.upload_date.desc()).all()
    
    # Get documents reviewed by this faculty member
    reviewed = Document.query.filter_by(
        assigned_faculty_id=current_user.id,
        reviewer_id=current_user.id,
        status='reviewed'
    ).order_by(Document.review_date.desc()).all()
    
    return render_template('faculty/dashboard.html',
                         pending_documents=documents,
                         reviewed_documents=reviewed)

@bp.route('/faculty/document/<int:id>')
@limiter.limit("100/hour")
@login_required
def view_document(id):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty only.', 'danger')
        return redirect(url_for('main.index'))
    
    document = Document.query.get_or_404(id)
    
    # Ensure faculty can only view documents assigned to them
    if document.assigned_faculty_id != current_user.id:
        logger.warning(f"Faculty {current_user.id} attempted to access unassigned document {id}")
        flash('Access denied. You can only view documents assigned to you.', 'danger')
        return redirect(url_for('faculty.dashboard'))
        
    student = User.query.get(document.uploader_id)
    
    return render_template('faculty/document.html',
                         document=document,
                         student=student)

@bp.route('/faculty/upload_review/<int:doc_id>', methods=['GET', 'POST'])
@limiter.limit(Config.UPLOAD_RATELIMIT)
@login_required
def upload_review(doc_id):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty only.', 'danger')
        return redirect(url_for('main.index'))
    
    document = Document.query.get_or_404(doc_id)
    
    # Ensure faculty can only review documents assigned to them
    if document.assigned_faculty_id != current_user.id:
        logger.warning(f"Faculty {current_user.id} attempted to review unassigned document {doc_id}")
        flash('Access denied. You can only review documents assigned to you.', 'danger')
        return redirect(url_for('faculty.dashboard'))
    
    if request.method == 'POST':
        review_files = []
        has_files = False
        
        # Handle both review file uploads
        for i in range(1, 3):
            if f'review_file_{i}' in request.files:
                file = request.files[f'review_file_{i}']
                if file and file.filename:
                    has_files = True
                    if not allowed_file(file.filename):
                        flash(f'Review file {i}: File type not allowed', 'danger')
                        return redirect(request.url)
                    review_files.append((i, file))
        
        if not has_files:
            flash('No review files selected', 'danger')
            return redirect(request.url)
        
        try:
            # Save review files
            for i, file in review_files:
                directory = f"reviews/document_{doc_id}"
                filename = save_file(file, directory)
                
                # Update document record
                if i == 1:
                    document.review_file1_path = os.path.join(directory, filename)
                else:
                    document.review_file2_path = os.path.join(directory, filename)
            
            # Update document status
            document.status = 'reviewed'
            document.reviewer_id = current_user.id
            document.review_date = datetime.utcnow()
            
            db.session.commit()
            
            # Send notification to student
            send_review_notification(document)
            
            flash('Review uploaded successfully', 'success')
            return redirect(url_for('faculty.dashboard'))
            
        except Exception as e:
            flash(f'Error uploading review: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('faculty/upload_review.html', document=document)

@bp.route('/faculty/reviewed')
@login_required
def reviewed_documents():
    if current_user.role != 'faculty':
        flash('Access denied. Faculty only.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all documents reviewed by current faculty
    documents = Document.query.filter_by(
        assigned_faculty_id=current_user.id,
        reviewer_id=current_user.id,
        status='reviewed'
    ).order_by(Document.review_date.desc()).all()
    
    return render_template('faculty/reviewed.html', documents=documents)
