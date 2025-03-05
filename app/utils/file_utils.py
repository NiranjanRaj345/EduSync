import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
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
    
    try:
        # Create directory if it doesn't exist (only once)
        os.makedirs(path, exist_ok=True)
        
        file_path = os.path.join(path, filename)
        file.save(file_path)
        logger.info(f"File saved successfully at: {file_path}")
        return filename
    except Exception as e:
        logger.error(f"Error saving file {filename}: {str(e)}")
        raise
