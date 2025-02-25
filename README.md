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
- **Database**: PostgreSQL (Neon)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login
- **Security**: Flask-Bcrypt
- **Email**: Flask-Mail
- **Hosting**: Koyeb

## Local Development

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- pip (Python package manager)

### Setup

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
```bash
cp .env.example .env
```
Edit `.env` with your local configuration.

5. **Initialize the database**
```bash
flask init-db
```

6. **Run the development server**
```bash
python run.py
```

## Deployment

### Prerequisites

1. [Koyeb Account](https://app.koyeb.com)
2. [Neon Account](https://neon.tech)
3. Git repository (e.g., GitHub)

### Database Setup with Neon

1. Create a new project in Neon
2. Create a new database
3. Get your connection string from the dashboard
4. Note: Neon provides PostgreSQL 15+ with automated backups and scaling

### Deployment to Koyeb

1. **Connect your repository**
   - Create a new app in Koyeb
   - Choose GitHub deployment method
   - Select your repository

2. **Configure environment variables**
   Set the following in Koyeb's environment variables:
   ```
   FLASK_APP=run.py
   FLASK_ENV=production
   DATABASE_URL=your-neon-database-url
   SECRET_KEY=your-secure-key
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email
   MAIL_PASSWORD=your-app-password
   ```

3. **Deploy**
   - Koyeb will automatically detect the Dockerfile
   - The application will be built and deployed
   - Database migrations will run automatically

### File Storage

For production deployment, consider these options for file storage:
1. Use S3 or similar cloud storage
2. Mount a persistent volume on Koyeb
3. Use a file hosting service

Current setup uses local file storage which is ephemeral on Koyeb. Implement cloud storage before production use.

### Monitoring and Maintenance

- Monitor application logs in Koyeb dashboard
- Set up Neon metrics monitoring
- Regular database backups (automated by Neon)
- Monitor application performance

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

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
