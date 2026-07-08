"""
app.py
------
This is the entry point of the whole project. Run this file to start the
server:

    python app.py

Then open http://127.0.0.1:5000 in your browser.

WHAT THIS FILE DOES (step by step):
1. Creates the Flask application object
2. Loads configuration from config.py
3. Connects the database (models.py) to the app
4. Registers the two "blueprints" (groups of routes):
     - api_bp        -> the REST API (routes/api.py)
     - dashboard_bp  -> the human moderator dashboard (routes/dashboard.py)
5. Creates the database tables if they don't exist yet
6. Starts the development server
"""

import os
from flask import Flask

from config import Config
from models import db
from routes.api import api_bp
from routes.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Connect SQLAlchemy (our ORM) to this Flask app
    db.init_app(app)

    # Register route groups
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard_bp)

    # Create all database tables (only creates them if missing - safe to
    # run every time the app starts)
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    # debug=True auto-reloads the server whenever you save a code change,
    # and shows detailed error pages - great for development.
    # Turn this off (debug=False) before deploying anywhere public.
    # Listen on 0.0.0.0 to accept connections from any network interface.
    # For production, set DEBUG=False and use a production WSGI server (gunicorn, etc.)
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", 5000))
    app.run(debug=True, host=host, port=port)
