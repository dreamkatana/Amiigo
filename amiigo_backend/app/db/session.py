from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base # Base will be imported from base_class

from app.core.config import settings # Import your settings

# Construct the database URL.
# This ensures that if SQLALCHEMY_DATABASE_URI is already fully formed in .env, it's used,
# otherwise, it's constructed from the individual PostgreSQL components.
if settings.SQLALCHEMY_DATABASE_URI and "://" in settings.SQLALCHEMY_DATABASE_URI : # Check if it's a full URI
    SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
elif settings.POSTGRES_USER and settings.POSTGRES_PASSWORD and settings.POSTGRES_SERVER and settings.POSTGRES_DB:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
else:
    # Fallback for local development if no specific PG settings or full URL is provided.
    SQLALCHEMY_DATABASE_URL = "sqlite:///./amiigo_local.db" # Use a file-based SQLite DB
    print(
        "Warning: PostgreSQL connection details not fully configured or full SQLALCHEMY_DATABASE_URI not provided. "
        f"Falling back to SQLite database: {SQLALCHEMY_DATABASE_URL}"
    )


# Create a SQLAlchemy engine instance.
# `pool_pre_ping=True` helps in handling connections that might have been closed by the DB server.
# `echo=settings.DEBUG` will log SQL queries if DEBUG is True in config.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create a SessionLocal class. This class will be used to create database sessions.
# - autocommit=False: Changes are not committed to the DB until session.commit() is called.
# - autoflush=False: Changes are not sent to the DB until explicitly flushed or committed.
# - bind=engine: Associates this session factory with our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions will be imported from `app.db.base_class.Base`.
# Models will inherit from it.

# Optional: Function to test database connection
def check_db_connection():
    """Tests the database connection by executing a simple query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        # Mask credentials in output
        db_display_url = SQLALCHEMY_DATABASE_URL.split('@')[-1] if '@' in SQLALCHEMY_DATABASE_URL else SQLALCHEMY_DATABASE_URL
        print(f"Successfully connected to the database: {db_display_url}")
        return True
    except Exception as e:
        db_display_url = SQLALCHEMY_DATABASE_URL.split('@')[-1] if '@' in SQLALCHEMY_DATABASE_URL else SQLALCHEMY_DATABASE_URL
        print(f"Database connection failed for URL {db_display_url}: {e}")
        return False

# This function will be used as a FastAPI dependency to provide a database session per request.
# It will be defined in `app.api.deps.py`.
# Example:
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# For standalone execution to test the connection (e.g., python -m app.db.session)
if __name__ == "__main__":
    # Mask credentials in output
    db_display_url = SQLALCHEMY_DATABASE_URL.split('@')[-1] if '@' in SQLALCHEMY_DATABASE_URL else SQLALCHEMY_DATABASE_URL
    print(f"Attempting to connect to database using URL (credentials masked): {db_display_url}")

    if not settings.POSTGRES_USER and not (settings.SQLALCHEMY_DATABASE_URI and "://" in settings.SQLALCHEMY_DATABASE_URI) :
        print("Hint: Ensure DATABASE_URL or POSTGRES_USER, POSTGRES_PASSWORD, etc. are set in your .env file for PostgreSQL.")
        # Accessing model_config like this might be version-specific for Pydantic.
        # For Pydantic v2, it's settings.model_config['env_file'] or settings.model_fields['model_config'].default.get('env_file')
        # A simpler way for this informational message is to just refer to the known path.
        env_file_path_from_config = getattr(settings.model_config, 'env_file', 'Not specified in model_config')
        print(f"Current .env file path used by config (if specified): {env_file_path_from_config}")


    check_db_connection()
# ``` # Removed offending backticks
