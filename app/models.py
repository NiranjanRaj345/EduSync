from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student or faculty
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploaded_documents = db.relationship(
        'Document',
        foreign_keys='Document.uploader_id',
        backref='uploader',
        lazy='dynamic'
    )
    assigned_documents = db.relationship(
        'Document',
        foreign_keys='Document.assigned_faculty_id',
        backref='assigned_faculty',
        lazy='dynamic'
    )
    reviewed_documents = db.relationship(
        'Document',
        foreign_keys='Document.reviewer_id',
        backref='reviewer',
        lazy='dynamic'
    )

    def set_password(self, password):
        """Set hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending_review')  # pending_review, reviewed
    
    # Google Drive fields
    gdrive_file_id = db.Column(db.String(100))
    gdrive_view_link = db.Column(db.String(255))
    
    # User relationships
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Review fields
    review_file1_path = db.Column(db.String(255))
    review_file2_path = db.Column(db.String(255))
    gdrive_review1_id = db.Column(db.String(100))
    gdrive_review2_id = db.Column(db.String(100))
    gdrive_review1_link = db.Column(db.String(255))
    gdrive_review2_link = db.Column(db.String(255))
    review_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Document {self.original_filename}>'

@login.user_loader
def load_user(id):
    """Load user by ID."""
    return User.query.get(int(id))
