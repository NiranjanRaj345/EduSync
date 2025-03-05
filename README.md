# EduSync

A document management system for educational institutions.

## Deployment on Render (Free Tier)

### Prerequisites

1. Render account (free tier)
2. Upstash Redis account (free tier)
3. Gmail account for SMTP (or alternative email service)

### Pre-deployment Setup

1. Create an Upstash Redis Database:
   - Sign up at [Upstash](https://upstash.com/)
   - Create a new Redis database
   - Copy the REST API URL and Token

2. Configure Email (Gmail):
   - Enable 2FA on your Gmail account
   - Generate an App Password
   - Save the password for configuration

### Environment Variables

Required environment variables in Render dashboard:

```bash
# Security
SECRET_KEY=<generate-a-secure-random-key>

# Redis Configuration
UPSTASH_REDIS_REST_URL=<your-upstash-redis-url>
UPSTASH_REDIS_REST_TOKEN=<your-upstash-redis-token>

# Email Configuration
MAIL_USERNAME=<your-gmail-address>
MAIL_PASSWORD=<your-gmail-app-password>
```

Note: DATABASE_URL will be automatically configured by Render

### Deployment Steps

1. Fork & Deploy:
   - Fork this repository to your GitHub account
   - Create a new Web Service in Render
   - Connect your GitHub repository
   - Select "Python" runtime
   - Keep the auto-detected build and start commands

2. Database Setup:
   - Render will automatically create and configure PostgreSQL
   - Database migrations will run automatically on deploy

3. Storage Configuration:
   - Disk will be automatically mounted at `/opt/render/project/src/uploads`
   - 1GB storage included in free tier

4. Environment Variables:
   - Add all required environment variables in Render dashboard
   - Ensure Redis and SMTP credentials are correct

### Features

- Async Redis session handling
- Secure file uploads
- Email notifications
- User role management
- Document review system

### Resource Limits (Free Tier)

- 512 MB RAM
- Shared CPU
- 1GB persistent disk
- Auto-sleep after 15 minutes of inactivity
- Auto-restart on error

### Monitoring

- Health check endpoint: `/`
- Logs available in Render dashboard
- Error tracking through application logs

### Development

```bash
# Clone repository
git clone https://github.com/yourusername/EduSync.git

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations

# Run development server
python run.py
```

### Testing Deployment

After deployment, verify:
1. User authentication works
2. File uploads succeed
3. Redis sessions persist
4. Email notifications send
5. Database migrations applied

For issues, check:
- Render logs
- Application logs
- Database connectivity
- Redis connection
- File permissions
