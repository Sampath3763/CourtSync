# app/__init__.py
import os
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from .models import db
from .config import config_by_name

# Initialize SocketIO without initial app
socketio = SocketIO(
    logger=True,
    engineio_logger=True,
    cors_allowed_origins="*",  # More permissive for development
    async_mode='eventlet',
    max_http_buffer_size=100 * 1024 * 1024  # 100MB for large file uploads
)

def _ensure_database_schema():
    """Ensure database schema is up to date with models."""
    try:
        from sqlalchemy import inspect
        
        # Check if we need to handle schema migrations
        inspector = inspect(db.engine)
        
        # Check if document table exists and has the required columns
        if 'document' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('document')]
            
            # If uploader_username column is missing, we need to recreate the schema
            if 'uploader_username' not in columns:
                print("Database schema mismatch detected. Updating schema...")
                
                # Drop and recreate all tables to ensure schema consistency
                db.drop_all()
                db.create_all()
                print("Database schema updated successfully.")
            else:
                print("Database schema is up to date.")
        else:
            # No tables exist, create them
            print("Creating database tables...")
            db.create_all()
            print("Database initialized successfully.")
            
    except Exception as e:
        print(f"Error ensuring database schema: {e}")
        # Fallback: try to create tables normally
        try:
            db.create_all()
        except Exception as fallback_error:
            print(f"Fallback database creation failed: {fallback_error}")
            raise

def create_app(config_name='default'):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, 
                instance_relative_config=True,
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    app.config.from_pyfile('config.py', silent=True)
    
    # Configure CORS
    CORS(app, 
         resources={r"/*": {"origins": "*"}},  # More permissive for development
         supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    
    # Initialize SocketIO with the app
    socketio.init_app(
        app,
        cors_allowed_origins="*",  # More permissive for development
        async_mode='eventlet',
        ping_timeout=60000,
        ping_interval=25000,
        transports=['websocket', 'polling'],
        max_http_buffer_size=100 * 1024 * 1024  # 100MB for large file uploads
    )

    # Create the upload folder if it doesn't exist
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200
        
    # Import and register blueprints and socket events
    with app.app_context():
        from . import routes, sockets
        
        # Handle database schema automatically
        _ensure_database_schema()

    return app