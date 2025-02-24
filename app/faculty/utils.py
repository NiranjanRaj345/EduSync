from flask import render_template
from flask_mail import Message
from app import mail, db
from app.models import User

def send_review_notification(document):
    """Send email notification to student when their document is reviewed"""
    try:
        # Get student info
        student = User.query.get(document.uploader_id)
        reviewer = User.query.get(document.reviewer_id)
        
        if not student or not reviewer:
            raise ValueError("Student or reviewer not found")
        
        # Create message
        msg = Message(
            f'Your document has been reviewed - {document.original_filename}',
            sender='noreply@university.edu',
            recipients=[student.email]
        )
        
        # Create email body
        msg.body = f"""
Dear {student.first_name} {student.last_name},

Your document "{document.original_filename}" has been reviewed by {reviewer.first_name} {reviewer.last_name}.

You can log in to your dashboard to view the feedback.

Best regards,
University Document System
        """
        
        # Create HTML version
        msg.html = render_template(
            'email/review_notification.html',
            student=student,
            document=document,
            reviewer=reviewer
        )
        
        # Send email
        mail.send(msg)
        
    except Exception as e:
        # Log error but don't stop the process
        print(f"Error sending notification email: {str(e)}")
