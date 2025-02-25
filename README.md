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

## Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd <repository-name>
```

2. **Set up PostgreSQL**
```sql
CREATE USER uploadmanager WITH PASSWORD 'uploadmanager0.0.1.1';
CREATE DATABASE document_system;
GRANT ALL PRIVILEGES ON DATABASE document_system TO uploadmanager;
```

3. **Create and activate a virtual environment**
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- Use default SECRET_KEY for development
- Default database URL: postgresql://uploadmanager:uploadmanager0.0.1.1@localhost:5432/document_system
- Configure email settings for notifications
- Adjust file upload settings if needed

6. **Initialize the database**
```bash
flask init-db
```

## Running the Application

1. **Start the development server**
```bash
python run.py
```

2. **Access the application**
Open your browser and navigate to:
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

## License

This project is licensed under the MIT License.
