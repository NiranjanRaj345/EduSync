from app import create_app, db
from app.models import User, Document

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

if __name__ == '__main__':
    app.run(debug=True)
