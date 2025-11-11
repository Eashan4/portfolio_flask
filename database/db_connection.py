import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# Centralized SQLAlchemy instance to be imported across the app
db = SQLAlchemy()

def init_db_app(app):
    # Configure database from environment or fallback to local MySQL
    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://ej:ej@localhost:3306/portfolio_flask",
    )
    
    # For Vercel/serverless: Use connection pooling and handle SSL
    # MySQL connections in serverless need proper handling
    if "mysql" in database_url.lower() and "localhost" not in database_url.lower():
        # Production MySQL (e.g., PlanetScale, AWS RDS) - may need SSL
        # Add SSL parameters if needed
        if "?" not in database_url:
            database_url += "?charset=utf8mb4"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,  # Recycle connections after 5 minutes
        "pool_size": 5,
        "max_overflow": 10
    }
    db.init_app(app)
    
    # Initialize database tables and migrate if needed
    with app.app_context():
        try:
            # Create all tables first
            db.create_all()
            
            # Check if project table exists, then migrate if needed
            try:
                # Check if project table exists
                result = db.session.execute(db.text("SHOW TABLES LIKE 'project'"))
                if result.fetchone():
                    # Table exists, check for missing columns
                    try:
                        # Check if esp_code column exists
                        result = db.session.execute(db.text("SHOW COLUMNS FROM project LIKE 'esp_code'"))
                        if result.fetchone() is None:
                            db.session.execute(db.text("ALTER TABLE project ADD COLUMN esp_code TEXT"))
                            db.session.commit()
                            print("✓ Added esp_code column to project table")
                    except Exception:
                        pass
                    
                    try:
                        # Check if custom_html column exists
                        result = db.session.execute(db.text("SHOW COLUMNS FROM project LIKE 'custom_html'"))
                        if result.fetchone() is None:
                            db.session.execute(db.text("ALTER TABLE project ADD COLUMN custom_html TEXT"))
                            db.session.commit()
                            print("✓ Added custom_html column to project table")
                    except Exception:
                        pass
            except Exception:
                # Table doesn't exist yet, db.create_all() will create it with all columns
                pass
                
        except Exception as e:
            # Log error but don't fail if there are issues
            print(f"Database initialization note: {e}")
