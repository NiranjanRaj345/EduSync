import os
import sys
from flask_migrate import upgrade
from app import create_app, db

def init_db():
    """Initialize the database"""
    try:
        app = create_app()
        
        # Push an application context
        with app.app_context():
            # Run migrations
            upgrade()
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                print(f"Created upload directory at {upload_dir}")
            
            print("Database initialization completed successfully.")
            return True
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
