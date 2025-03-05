from app import create_app
from asgiref.wsgi import WsgiToAsgi

flask_app = create_app()
app = WsgiToAsgi(flask_app)

if __name__ == "__main__":
    flask_app.run()
