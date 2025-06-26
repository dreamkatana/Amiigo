import pytest
from typing import Generator, Any

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.pool import StaticPool # Useful for SQLite in-memory for tests

from app.main import app # Main FastAPI application
from app.db.base_class import Base # SQLAlchemy Base for creating tables
from app.db.session import SessionLocal, SQLALCHEMY_DATABASE_URL # Original SessionLocal and DB URL
from app.api.deps import get_db # The dependency we want to override

# --- Test Database Setup ---
# For testing, it's common to use a separate database or an in-memory SQLite database.
# If using a separate test PostgreSQL database, ensure its URL is configured (e.g., via environment variables).

# Example for a dedicated test PostgreSQL database (ensure this DB exists and user has rights)
# TEST_SQLALCHEMY_DATABASE_URL = "postgresql://testuser:testpassword@localhost:5432/amiigo_test_db"
# If you want to use the same DB but ensure cleanup, be very careful.
# For true isolation, a separate DB or schema is best.

# For SQLite in-memory (simpler for local testing, but might not catch all PG-specific issues):
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # File-based SQLite for persistence between test runs if needed
# TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" # In-memory SQLite (faster, but data lost after test run)

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    # For SQLite in-memory, connect_args are needed for multithreading if TestClient runs in threads
    connect_args={"check_same_thread": False} if "sqlite" in TEST_SQLALCHEMY_DATABASE_URL else {},
    # poolclass=StaticPool, # Use StaticPool if using SQLite in-memory to ensure same connection
    echo=False # Don't echo SQL for tests unless debugging
)

# Create a new sessionmaker for the test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Fixture to Create and Drop Tables ---
@pytest.fixture(scope="session", autouse=True) # Changed scope to session for create/drop once
def setup_test_db():
    """
    Set up the test database: create all tables before tests run, drop them after.
    `autouse=True` makes this fixture run automatically for the session.
    """
    # Create all tables in the test database
    # This requires all your models to be imported somewhere (e.g., in app.models.__init__)
    # so that Base.metadata knows about them.
    Base.metadata.create_all(bind=engine)
    print(f"Test database tables created at {TEST_SQLALCHEMY_DATABASE_URL}")

    yield # Tests run here

    # Drop all tables after tests are done
    Base.metadata.drop_all(bind=engine)
    print(f"Test database tables dropped from {TEST_SQLALCHEMY_DATABASE_URL}")


# --- Fixture to Override `get_db` Dependency ---
@pytest.fixture(scope="function") # function scope: new DB session for each test
def db_session() -> Generator[Session, None, None]:
    """
    Pytest fixture to provide a database session for tests.
    This session uses the test database.
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    yield db

    db.close()
    transaction.rollback() # Rollback changes after each test to keep DB clean
    connection.close()


# --- Fixture for Test Client ---
@pytest.fixture(scope="function") # Changed scope to function
def client(db_session: Session) -> Generator[TestClient, None, None]: # db_session here will be function scoped for each test using client
    """
    Pytest fixture to provide a FastAPI TestClient.
    Overrides the `get_db` dependency to use the test database session.
    """

    # This override function will be called for each request during a test.
    # It needs to yield the db_session that is specific to that test function's scope.
    def override_get_db() -> Generator[Session, None, None]:
        """Dependency override for get_db to use the test session."""
        # Pytest fixtures are managed such that when 'client' (module scope)
        # is used by a test function, and 'client' itself depends on 'db_session' (function scope),
        # 'db_session' is invoked for that specific test function.
        # So, the 'db_session' instance available here inside 'override_get_db'
        # is the one pertaining to the current test execution context.
        try:
            yield db_session
        finally:
            # The db_session fixture itself handles closing/rolling back.
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    del app.dependency_overrides[get_db]


# --- Utility Fixtures (Optional) ---

@pytest.fixture(scope="module")
def test_superuser_token_headers(client: TestClient) -> dict[str, str]:
    """
    Fixture to get authentication token headers for a superuser.
    Placeholder: Implement actual superuser creation and login.
    """
    print("Warning: `test_superuser_token_headers` fixture is a placeholder.")
    return {"Authorization": "Bearer fake_superuser_token"}


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    """
    Fixture to get authentication token headers for a normal user.
    Placeholder: Specific tests should manage their own user creation and login for tokens.
    """
    print("Warning: `normal_user_token_headers` fixture is a placeholder for general use.")
    return {"Authorization": "Bearer fake_normal_user_token"}

# General Notes for conftest.py:
# - Using a file-based SQLite 'test.db' for persistence during a test session.
# - 'setup_test_db' (session scope, autouse) creates/drops tables once per test session.
# - 'db_session' (function scope) provides a clean, rolled-back transaction per test.
# - 'client' (module scope) fixture overrides 'get_db' to inject the function-scoped 'db_session'.
#   This ensures that each test using the client operates on a fresh DB transaction.
# - Token header fixtures are placeholders; real implementations would involve creating users
#   and logging them in via the API or utility functions.
# - The self-correction notes that were previously here have been removed to prevent syntax issues.
#   Key points from those notes included:
#   - Using session scope for DB setup/teardown for efficiency.
#   - Ensuring db_session provides transactional integrity per test.
#   - Using connect_args={"check_same_thread": False} for SQLite.
#   - Using a file-based SQLite for easier inspection if needed.
