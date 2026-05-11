from flask import Flask, request, abort
from flask_cors import CORS
from app.config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    API_KEY = os.getenv("SECRET_KEY", "secret_cadangan")
    
    # Security with SECRET_KEY
    # @app.before_request
    # def validate_api_key():
    #     incoming_key = request.headers.get("X-Internal-Key")
    #     print(incoming_key)

    #     if incoming_key != API_KEY:
    #         abort(401, description="Unauthorized")


    # Register Blueprints

    # add the import here
    from app.opening_part.routes import opening_bp
    from app.pole.routes import pole_bp

    # add the blueprint here
    app.register_blueprint(opening_bp)
    app.register_blueprint(pole_bp)

    return app