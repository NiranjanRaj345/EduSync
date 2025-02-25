import os
from app import create_app, db
from app.models import User, Document
from flask_migrate import upgrade as upgrade_database

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell for testing"""
    return {
        'db': db,
        'User': User,
        'Document': Document
    }

@app.cli.command("init-db")
def init_db():
    """Initialize the database (create tables)"""
    db.create_all()
    print("Database initialized.")

# Perform database migrations on startup
with app.app_context():
    upgrade_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
