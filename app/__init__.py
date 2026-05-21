from flask import Flask, jsonify, request
from flask_cors import CORS
from app.config import Config
import os
from datetime import datetime, timezone

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    API_KEY = os.getenv("SECRET_KEY", "secret_cadangan")
    
    # Security with SECRET_KEY PENTING JANGAN DI HAPUS
    # @app.before_request
    # def validate_api_key():
    #     incoming_key = request.headers.get("X-Internal-Key")
    #     print(incoming_key)

    #     if incoming_key != API_KEY:
    #         abort(401, description="Unauthorized")

    # ganti "*" di origin dengan URL Railway API Gateway
    # CORS(app, resources={r"/api/*": {"origins": "*"}})\


    """Entry Point Start"""
    @app.route("/")
    def root():
        return jsonify({
            "name": "Kori Bali Calculation Service",
            "status": "online",
            "version": "1.0.0",
            "server_time": datetime.now(timezone.utc).isoformat()
        })

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy"
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Route not found",
            "path": request.path
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error"
        }), 500
    """Entry Point End"""
    

    # Register Blueprints

    # add the import here
    from app.opening_part.routes import opening_bp
    from app.pole.routes import pole_bp
    from app.load_object.routes import load_object_bp

    # add the blueprint here
    app.register_blueprint(opening_bp)
    app.register_blueprint(pole_bp)
    app.register_blueprint(load_object_bp)

    return app