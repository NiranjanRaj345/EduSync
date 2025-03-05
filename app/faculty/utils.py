from flask import render_template, current_app
from flask_mail import Message
from app import mail, db
from app.models import User
import logging
import asyncio
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=3)

def retry_on_error(retries=3, delay=1):
    """Decorator for retrying operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Operation failed (attempt {attempt + 1}/{retries}): {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
            logger.error(f"Operation failed after {retries} attempts: {str(last_error)}")
            raise last_error
        return wrapper
    return decorator

def send_mail_sync(msg):
    """Synchronous mail sending for use with executor"""
    try:
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

@retry_on_error()
async def send_review_notification(document):
    """Send email notification to student when their document is reviewed"""
    try:
        # Get student info with error handling
        student = User.query.get(document.uploader_id)
        reviewer = User.query.get(document.reviewer_id)
        
        if not student:
            raise ValueError(f"Student not found for document {document.id}")
        if not reviewer:
            raise ValueError(f"Reviewer not found for document {document.id}")
        
        if not student.email:
            raise ValueError(f"No email address for student {student.id}")
        
        # Create message
        msg = Message(
            subject=f'Your document has been reviewed - {document.original_filename}',
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@university.edu'),
            recipients=[student.email]
        )
        
        # Create email body with error handling
        try:
            msg.html = render_template(
                'email/review_notification.html',
                student=student,
                document=document,
                reviewer=reviewer
            )
            
            # Plain text fallback
            msg.body = f"""
Dear {student.first_name} {student.last_name},

Your document "{document.original_filename}" has been reviewed by {reviewer.first_name} {reviewer.last_name}.

You can log in to your dashboard to view the feedback.

Best regards,
University Document System
            """
        except Exception as e:
            logger.error(f"Failed to render email template: {str(e)}")
            raise
        
        # Send email asynchronously using thread pool
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(executor, send_mail_sync, msg)
        
        if success:
            logger.info(f"Review notification sent successfully to {student.email}")
        else:
            raise Exception("Failed to send email notification")
            
    except Exception as e:
        logger.error(f"Error in send_review_notification: {str(e)}")
        raise
