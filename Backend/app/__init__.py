from flask import Flask
from flask_cors import CORS
from .routes import main  # Import your blueprint

def create_app():
    app = Flask(__name__)

    # Enable CORS for the entire app
    CORS(app)

    # Register the blueprint (routes)
    app.register_blueprint(main)

    return app
