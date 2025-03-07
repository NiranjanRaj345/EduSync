# EduSync

## Deployment on Railway

### 1. Environment Variables
Set these in your Railway dashboard:
```
FLASK_ENV=production
DATABASE_URL=your_postgres_url
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
SECRET_KEY=your_secret_key
```

### 2. Start Command
The application uses gevent worker for better async handling:
```bash
gunicorn "app:create_app()" --workers 4 --worker-class=gevent --worker-connections=1000 --timeout 120 --access-logfile - --error-logfile -
```

### 3. Migration Instructions

If you're migrating from aiohttp worker:

1. Update your requirements.txt (already included):
```
gunicorn[gevent]==21.2.0
greenlet>=2.0.2
```

2. Update your start command in Railway dashboard:
   - Remove `--worker-class aiohttp.worker.GunicornWebWorker`
   - Add `--worker-class=gevent --worker-connections=1000`

3. Deploy the changes:
```bash
git add .
git commit -m "Switch to gevent workers for better async compatibility"
git push railway main
```

### 4. Verification

After deployment, verify:
1. Application starts without worker errors
2. Session handling works correctly
3. Async operations (Redis, file uploads) function properly
4. Database connections work as expected
5. WebSocket connections (if any) function properly

If you see any issues:
1. Check Railway logs for errors
2. Verify environment variables are set correctly
3. Ensure database migrations are up to date
4. Check Redis connection is working

## Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in .env:
```
FLASK_ENV=development
DATABASE_URL=your_local_db_url
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
```

4. Run migrations:
```bash
flask db upgrade
```

5. Run development server:
```bash
python run.py
```

## Architecture Notes

### Worker Configuration
- Uses gevent worker for production
- 4 worker processes for better concurrency
- 1000 connections per worker
- 120 second timeout for long-running operations

### Async Handling
- Development mode uses uvloop for better async performance
- Production mode uses gevent for compatibility and performance
- Redis operations are handled asynchronously
- Session data is stored in Redis with proper security measures

### Performance
- Connection pooling for database
- Redis connection management
- Proper session handling
- Async operations where beneficial
- Gevent for non-blocking I/O

### Security
- Secure session configuration
- CSRF protection
- Rate limiting
- Secure cookie settings
- Environment-based security settings

### Monitoring
- Access and error logging
- Application-level logging
- Redis operation logging
- Database transaction logging
