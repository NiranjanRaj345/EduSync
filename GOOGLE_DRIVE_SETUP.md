# Google Drive Integration Setup Guide

This guide will walk you through setting up Google Drive integration using a service account.

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Create Project" or select an existing project
3. Note down your Project ID

## 2. Enable the Google Drive API

1. In the Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click "Enable"

## 3. Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `edusync-storage` (or your preferred name)
   - Description: "Service account for EduSync document storage"
   - Click "Create"

4. Skip role selection (we'll handle permissions through Drive sharing)
5. Click "Done"

## 4. Generate Service Account Key

1. In the service accounts list, click on your newly created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Click "Create"
6. Save the downloaded JSON file as `service-account.json` in your project root

## 5. Set Up Google Drive Folder

1. Create a new folder in Google Drive where documents will be stored
2. Right-click the folder > "Share"
3. Copy the service account email (found in `service-account.json` under `client_email`)
4. Add the service account email as an editor
5. Copy the folder ID from the URL:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```

## 6. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update these settings:
   ```
   USE_GOOGLE_DRIVE=True
   GOOGLE_DRIVE_CREDENTIALS=service-account.json
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
   ```

## 7. Verify Setup

1. Ensure `service-account.json` is in your project root
2. Make sure the file is listed in `.gitignore`
3. Test the setup:
   ```bash
   flask run
   ```
4. Try uploading a document through the application

## Directory Structure

Your project should look like this:
```
project_root/
├── .env
├── service-account.json
├── .gitignore
└── app/
    └── ...
```

## Security Notes

1. Never commit `service-account.json` to version control
2. Keep the service account key secure
3. Use minimal necessary permissions
4. Regularly monitor service account usage

## Troubleshooting

### Permission Issues

If you get permission errors:
1. Verify the service account email is correct
2. Check folder sharing settings
3. Ensure the Google Drive API is enabled
4. Verify the JSON key file is valid and readable

### File Access Issues

If files aren't accessible:
1. Check if files are in the correct folder
2. Verify folder ID in `.env`
3. Ensure service account has editor access

### Configuration Issues

If the integration isn't working:
1. Verify `USE_GOOGLE_DRIVE=True` in `.env`
2. Check path to `service-account.json` is correct
3. Ensure all required environment variables are set

## Maintenance

1. Monitor service account usage in Google Cloud Console
2. Regularly check file permissions
3. Review access logs periodically
4. Keep service account key secure
5. Update credentials if compromised

For additional help, refer to:
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Google Drive API Documentation](https://developers.google.com/drive)
