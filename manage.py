from app import create_app, db
from app.models import User, Document

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Configure Flask shell context."""
    return {
        'db': db,
        'User': User,
        'Document': Document
    }

def initialize_app():
    """Initialize the application with required setup."""
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Run migrations
        from flask_migrate import upgrade
        upgrade()

if __name__ == '__main__':
    initialize_app()
    app.run()
