# University Document Upload & Review System

A secure platform that allows students to upload documents and faculty members to review and provide feedback.

## Features

- 🔐 Role-based authentication (Students & Faculty)
- 📄 Document upload system for students
- 👨‍🏫 Review system for faculty members
- 📧 Email notifications for review updates
- 🔍 Document tracking system
- 🎯 Clean and responsive UI

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login
- **Security**: Flask-Bcrypt
- **Email**: Flask-Mail

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- pip (Python package manager)

## Setup Instructions

1. **Clone the repository**

```bash
git clone <repository-url>
cd <repository-name>
```

2. **Create and activate a virtual environment**

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

For security purposes, environment variables are not committed to version control. You'll need to:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   - Generate a secure SECRET_KEY
   - Configure your PostgreSQL database URL
   - Set up your email credentials (for notifications)
   - Adjust file upload settings if needed

The `.env` file is gitignored to prevent sensitive credentials from being exposed in version control.

5. **Initialize the database**

```bash
flask init-db
```

## Running the Application

1. **Start the development server**

```bash
python run.py
```

2. **Access the application**

Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth/
│   ├── main/
│   ├── student/
│   ├── faculty/
│   └── templates/
├── uploads/
├── .env
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

## Usage

1. **Student Workflow**
   - Register as a student
   - Log in to your account
   - Upload documents
   - Track document review status
   - View faculty feedback

2. **Faculty Workflow**
   - Register as faculty
   - Log in to your account
   - View pending documents
   - Review documents
   - Upload feedback files

## Security Features

- Password hashing using bcrypt
- CSRF protection
- Secure file uploads
- Role-based access control
- Session management

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Deployment on Railway

### Prerequisites

1. A GitHub account
2. Install Railway CLI (optional):
   ```bash
   npm i -g @railway/cli
   ```
3. Create a Railway account at https://railway.app/ (Sign in with GitHub)

### Deployment Steps

1. **Fork and Push to GitHub**
   - Fork this repository
   - Push your changes to your fork
   - Ensure your repository is public

2. **Create Railway Project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the Dockerfile

3. **Add PostgreSQL Database**
   - In your project dashboard, click "New Service"
   - Select "Database"
   - Choose "PostgreSQL"
   - Railway will provide the connection details automatically

4. **Configure Environment Variables**
   - Go to project settings
   - Add the following variables:
     ```
     FLASK_APP=run.py
     FLASK_ENV=production
     SECRET_KEY=<your-secure-key>
     MAIL_SERVER=smtp.gmail.com
     MAIL_PORT=587
     MAIL_USE_TLS=True
     MAIL_USERNAME=<your-email>
     MAIL_PASSWORD=<your-app-password>
     ```
   - Database URL will be automatically added by Railway

5. **Monitor Deployment**
   - Railway will automatically deploy your application
   - Monitor the deployment logs in the dashboard
   - Once complete, click on the generated domain to access your app

### File Storage on Railway

Since Railway's filesystem is ephemeral, for production use:
1. Use AWS S3 or similar for file storage
2. Or use Railway's Volume Service (Beta)
3. For development/testing, files will be stored temporarily

### Useful Railway Commands
```bash
# Login to Railway
railway login

# Link to your project
railway link

# Deploy manually (if needed)
railway up

# View logs
railway logs

# List running services
railway status
```

### Monitoring and Maintenance
- Monitor application logs in Railway dashboard
- Set up alerts for errors
- Keep track of free tier usage (500 hours/month)
- Backup your database regularly

## License

This project is licensed under the MIT License.
