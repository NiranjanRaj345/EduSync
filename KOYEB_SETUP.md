# Koyeb Deployment Setup Guide

## Required Secrets

Before deploying to Koyeb, you need to set up the following secrets:

1. **GOOGLE_DRIVE_CREDENTIALS_B64**
   ```bash
   # First, encode your service account credentials
   python3 encode_credentials.py service-account.json
   
   # This will output a long base64 string that looks like:
   # ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCI...
   
   # Copy the entire string (excluding any other output text)
   # The string starts with "ewo" and ends with "Cg=="
   
   # In Koyeb dashboard:
   # 1. Go to Secrets
   # 2. Click "Create Secret"
   # 3. Name: GOOGLE_DRIVE_CREDENTIALS_B64
   # 4. Value: Paste the entire base64 string
   # 5. Click Create
   
   # The application will automatically decode this at runtime
   ```

2. **GOOGLE_DRIVE_FOLDER_ID**
   - Create a folder in Google Drive
   - Share it with the service account email
   - Copy the folder ID from the URL
   ```
   # URL format: https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```

3. **SECRET_KEY**
   ```bash
   # Generate a secure random key
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **DATABASE_URL**
   ```
   # Format: postgresql://username:password@host:port/database
   ```

5. **REDIS_URL**
   ```
   # Format: redis://default:password@host:port
   ```

6. **MAIL_USERNAME** and **MAIL_PASSWORD**
   - Gmail account username
   - App-specific password for Gmail

## Creating Secrets in Koyeb

1. Go to Koyeb Dashboard
2. Navigate to Secrets section
3. Create each secret:
   - Click "Create Secret"
   - Name: Use the exact names above
   - Value: Paste the corresponding value
   - Click "Create"

## Deployment Steps

1. Install Koyeb CLI:
   ```bash
   curl -fsSL https://cli.koyeb.com/install.sh | bash
   ```

2. Login to Koyeb:
   ```bash
   koyeb login
   ```

3. Deploy the application:
   ```bash
   koyeb app init edusync
   ```

4. Verify deployment:
   ```bash
   koyeb service status edusync
   ```

5. View logs:
   ```bash
   koyeb service logs edusync
   ```

## Monitoring Health

The application includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-02-28T12:00:00Z",
  "google_drive": true,
  "database": true,
  "upload_folder": true
}
```

## Troubleshooting

1. **Database Connection Issues**
   - Check DATABASE_URL secret
   - Verify database accessibility from Koyeb
   - Check logs for connection errors

2. **Google Drive Issues**
   - Verify GOOGLE_DRIVE_CREDENTIALS_B64 is correctly encoded
   - Check service account permissions
   - Verify folder sharing settings

3. **File Upload Issues**
   - Check upload folder permissions
   - Verify UPLOAD_FOLDER path in configuration
   - Check file size limits

4. **Email Issues**
   - Verify MAIL_USERNAME and MAIL_PASSWORD
   - Check Gmail account settings
   - Verify TLS settings

## Maintenance

1. **Database Migrations**
   ```bash
   # Connect to instance
   koyeb shell edusync
   
   # Run migrations
   flask db upgrade
   ```

2. **Updating Secrets**
   ```bash
   # Update secret value
   koyeb secret update SECRET_NAME -v "new_value"
   ```

3. **Restarting Service**
   ```bash
   koyeb service restart edusync
   ```

4. **Checking Logs**
   ```bash
   # View real-time logs
   koyeb service logs edusync -f
   ```

## Important Notes

1. Always use environment variables for sensitive data
2. Keep service account key secure
3. Monitor application logs regularly
4. Set up backup procedures for database
5. Configure rate limiting appropriately
6. Monitor Google Drive quota usage
