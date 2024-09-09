from flask import Flask
from app.routes import receipt_routes

def create_app():
    app = Flask(__name__)

    # Register Blueprints if needed
    app.register_blueprint(receipt_routes)

    return app

