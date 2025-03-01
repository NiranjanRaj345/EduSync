from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from flask import current_app
import logging
from . import db, login_manager

logger = logging.getLogger(__name__)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'faculty'
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploaded_documents = db.relationship('Document', backref='uploader', lazy=True,
                                      foreign_keys='Document.uploader_id')
    assigned_documents = db.relationship('Document', backref='assigned_faculty', lazy=True,
                                      foreign_keys='Document.assigned_faculty_id')
    reviewed_documents = db.relationship('Document', backref='reviewer', lazy=True,
                                       foreign_keys='Document.reviewer_id')

    def __repr__(self):
        return f'<User {self.email}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending_review')  # pending_review, reviewed
    
    # Foreign Keys
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Review Documents
    review_file1_path = db.Column(db.String(512), nullable=True)
    review_file2_path = db.Column(db.String(512), nullable=True)
    review_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'

@login_manager.user_loader
def load_user(user_id):
    retries = 3
    while retries > 0:
        try:
            return User.query.get(int(user_id))
        except OperationalError as e:
            retries -= 1
            logger.warning(f"Database connection error, retries left: {retries}. Error: {str(e)}")
            if retries == 0:
                logger.error(f"Failed to load user after 3 retries. Error: {str(e)}")
                return None
        except SQLAlchemyError as e:
            logger.error(f"Database error while loading user: {str(e)}")
            return None
