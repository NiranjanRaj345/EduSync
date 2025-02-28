# Document Management System with Google Drive Integration

A document management system for educational institutions that supports both local storage and Google Drive for file management.

## Features

- Upload and manage student documents
- Faculty review system with feedback files
- Google Drive integration for cloud storage
- Local storage fallback option
- Email notifications for document reviews
- Secure file access control

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your configuration settings.

3. Set up Google Drive integration:
Follow the instructions in `GOOGLE_DRIVE_SETUP.md`

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the development server:
```bash
flask run
```

## Production Deployment

1. Prepare server:
   - Ubuntu 22.04 or later
   - Python 3.12
   - PostgreSQL 14 or later
   - Redis 6 or later
   - Nginx

2. Clone repository:
```bash
git clone https://github.com/yourusername/edusync.git /var/www/edusync
cd /var/www/edusync
```

3. Configure deployment:
   - Update domain in `nginx.conf`
   - Update `.env` with production settings
   - Configure `service-account.json` for Google Drive
   - Set production database credentials

4. Run deployment script:
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

5. Post-deployment tasks:
   - Follow the checklist in `PRODUCTION_CHECKLIST.md`
   - Set up monitoring and alerts
   - Configure backup schedule
   - Test all functionality

For detailed deployment instructions, see:
- `PRODUCTION_CHECKLIST.md`: Pre-deployment checklist
- `GOOGLE_DRIVE_SETUP.md`: Google Drive configuration
- `nginx.conf`: Web server configuration
- `gunicorn.conf.py`: Application server settings
- `edusync.service`: Systemd service configuration

## Usage

### File Storage Options

The system supports two storage modes:

1. Local Storage (default):
- Files are stored in the `uploads/` directory
- Set `USE_GOOGLE_DRIVE=False` in `.env`

2. Google Drive Storage:
- Files are stored in Google Drive
- Set `USE_GOOGLE_DRIVE=True` in `.env`
- Requires proper Google Drive credentials setup

### Document Upload Process

1. Students:
- Log in as student
- Navigate to dashboard
- Click "Upload New Document"
- Select file and assigned faculty
- Submit for review

2. Faculty:
- Log in as faculty
- View assigned documents
- Download and review student documents
- Upload feedback files
- Students get email notifications

### Security Features

- File access control based on user roles
- Secure file storage paths
- Google Drive integration with OAuth 2.0
- Rate limiting for uploads
- Input validation and sanitization

### Directory Structure

```
├── app/
│   ├── uploads/          # Local storage directory
│   │   ├── student_*/    # Student documents
│   │   ├── reviews/      # Faculty review files
│   │   └── temp/        # Temporary storage for uploads
│   └── utils/
│       └── google_drive.py  # Google Drive integration
```

## Configuration Options

### Environment Variables

- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `UPLOAD_FOLDER`: Local upload directory path
- `USE_GOOGLE_DRIVE`: Enable/disable Google Drive storage
- `GOOGLE_DRIVE_CREDENTIALS`: Path to credentials file
- `GOOGLE_DRIVE_TOKEN`: Path to token file
- `MAIL_*`: Email configuration settings

## Troubleshooting

1. Google Drive Authorization:
- Ensure `service-account.json` is present
- Verify service account has necessary permissions
- Check target folder sharing settings

2. File Upload Issues:
- Verify upload directory permissions
- Check file size limits
- Ensure proper mime types

3. Database Migrations:
- Run `flask db upgrade` for schema updates
- Check database connection settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.
