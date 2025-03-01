import os
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging
import json
import tempfile
import io

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
            b64_creds = os.getenv('GOOGLE_DRIVE_CREDENTIALS_B64')
            
            if not b64_creds:
                logger.error("GOOGLE_DRIVE_CREDENTIALS_B64 environment variable not set")
                raise ValueError("Google Drive credentials not configured")
            
            try:
                # Decode base64 credentials
                creds_json = base64.b64decode(b64_creds)
                creds_dict = json.loads(creds_json)
                
                # Create credentials from parsed JSON directly
                try:
                    credentials = service_account.Credentials.from_service_account_info(
                        creds_dict,
                        scopes=SCOPES
                    )
                except Exception as e:
                    logger.error(f"Error creating credentials from service account info: {str(e)}")
                    raise
                
            except Exception as e:
                logger.error(f"Error processing credentials: {str(e)}")
                raise
            
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Error building Drive service: {str(e)}")
            raise

    def upload_file(self, file_path: str, filename: str, mime_type: str = 'application/pdf') -> tuple[str, str]:
        """
        Uploads a file to Google Drive.
        
        Args:
            file_path: Path to the file to upload
            filename: Name for the file in Google Drive
            mime_type: MIME type of the file
            
        Returns:
            tuple: (file_id, web_view_link)
            
        Raises:
            ValueError: If the file does not exist or credentials are not configured
            IOError: If there are issues reading the file
            Exception: For other Google Drive API errors
        """
        try:
            file_metadata = {
                'name': filename,
                'parents': [os.getenv('GOOGLE_DRIVE_FOLDER_ID')] if os.getenv('GOOGLE_DRIVE_FOLDER_ID') else None
            }
            # Remove None values from metadata
            file_metadata = {k: v for k, v in file_metadata.items() if v is not None}
            
            # Ensure the service is initialized
            if not self._service:
                self._service = self._get_service()
            
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

    def delete_file(self, file_id: str) -> None:
        """
        Deletes a file from Google Drive.
        
        Args:
            file_id: The ID of the file to delete
            
        Raises:
            ValueError: If credentials are not configured
            Exception: For Google Drive API errors
        """
        try:
            if not self._service:
                self._service = self._get_service()
            self._service.files().delete(fileId=file_id).execute()
            logger.info(f"File with ID {file_id} deleted from Google Drive")
        except Exception as e:
            logger.error(f"Error deleting file from Google Drive: {str(e)}")
            raise

    def get_file_url(self, file_id: str) -> str:
        """
        Gets the web view URL for a file.
        
        Args:
            file_id: The ID of the file
            
        Returns:
            str: The web view URL for the file
            
        Raises:
            ValueError: If credentials are not configured
            Exception: For Google Drive API errors
        """
        try:
            if not self._service:
                self._service = self._get_service()
            file = self._service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            return file.get('webViewLink')
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            raise

gdrive = GoogleDriveService()
