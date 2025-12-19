import os
from flask import Flask
from flask_cors import CORS
from config import Config
from routes import analyze_bp

def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(analyze_bp)
    
    # Ensure temp upload folder exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    return app

app = create_app()

if __name__ == '__main__':
    print("🏥 Doclyst Backend Starting...")
    print("📍 API Endpoint: http://localhost:5000/analyze")
    print("💡 Health Check: http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)
