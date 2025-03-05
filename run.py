import os
from app import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    if os.environ.get("FLASK_ENV") == "development":
        # Use Uvicorn directly in development
        uvicorn.run(
            "run:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="debug",
            workers=1
        )
    else:
        # In production, Gunicorn manages Uvicorn workers
        app.run(host="0.0.0.0", port=port)
