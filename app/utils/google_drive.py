import os
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging
import json
import tempfile

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveService:
    _instance = None
    _service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GoogleDriveService, cls).__new__(cls)
            cls._instance._service = cls._instance._get_service()
        return cls._instance

    def _get_service(self):
        """Creates Drive API service using service account credentials or base64 encoded credentials."""
        try:
            credentials = None
            # Check for base64 encoded credentials first (for Koyeb)
            b64_creds = os.getenv('GOOGLE_DRIVE_CREDENTIALS_B64')
            if b64_creds:
                logger.info("Using base64 encoded credentials")
                creds_json = base64.b64decode(b64_creds)
                with tempfile.NamedTemporaryFile(mode='w+') as tmp:
                    tmp.write(creds_json.decode('utf-8'))
                    tmp.flush()
                    credentials = service_account.Credentials.from_service_account_file(
                        tmp.name,
                        scopes=SCOPES
                    )
            else:
                # Fall back to file-based credentials
                logger.info("Using file-based credentials")
                credentials = service_account.Credentials.from_service_account_file(
                    os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'service-account.json'),
                    scopes=SCOPES
                )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Error building Drive service: {str(e)}")
            raise

    def upload_file(self, file_path, filename, mime_type='application/pdf'):
        """Uploads a file to Google Drive.
        
        Args:
            file_path: Local path to the file to upload
            filename: Name to give the file in Google Drive
            mime_type: MIME type of the file
            
        Returns:
            Tuple containing (file_id, web_view_link)
        """
        try:
            file_metadata = {
                'name': filename,
                'parents': [os.getenv('GOOGLE_DRIVE_FOLDER_ID')] if os.getenv('GOOGLE_DRIVE_FOLDER_ID') else None
            }
            # Remove None values from metadata
            file_metadata = {k: v for k, v in file_metadata.items() if v is not None}
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self._service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            logger.info(f"File {filename} uploaded to Google Drive with ID: {file.get('id')}")
            return file.get('id'), file.get('webViewLink')
            
        except Exception as e:
            logger.error(f"Error uploading file to Google Drive: {str(e)}")
            raise

    def delete_file(self, file_id):
        """Deletes a file from Google Drive.
        
        Args:
            file_id: ID of the file to delete
        """
        try:
            self._service.files().delete(fileId=file_id).execute()
            logger.info(f"File with ID {file_id} deleted from Google Drive")
        except Exception as e:
            logger.error(f"Error deleting file from Google Drive: {str(e)}")
            raise

    def get_file_url(self, file_id):
        """Gets the web view URL for a file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            Web view URL for the file
            
        Note:
            The service account must have permission to access the file.
            Share the parent folder with the service account email address.
        """
        try:
            file = self._service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            return file.get('webViewLink')
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            raise

gdrive = GoogleDriveService()
