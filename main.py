import logging
import os
from app import app, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Initialize database tables
        with app.app_context():
            db.create_all()
        
        # Run the Flask application
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to prevent double execution
        )
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
