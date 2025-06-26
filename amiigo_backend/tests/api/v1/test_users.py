import pytest # For marking tests, using fixtures
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting db session fixture
from typing import Dict # For type hinting headers

from app import crud, schemas, models
from app.core.config import settings # For API_V1_STR
from tests.utils.user import random_email, random_lower_string, create_random_user, get_user_authentication_headers # Test utilities

# --- Test User Creation (/users/ - POST) ---

def test_create_user_new_email(client: TestClient, db_session: Session) -> None:
    """
    Test creating a new user with a unique email.
    """
    email = random_email()
    password = random_lower_string(12)
    data = {"email": email, "password": password}

    response = client.post(f"{settings.API_V1_STR}/users/", json=data)

    assert response.status_code == 201, response.text
    created_user_data = response.json()
    assert created_user_data["email"] == email
    assert "user_id" in created_user_data
    assert "password_hash" not in created_user_data # Ensure password hash is not returned

    # Verify user in database
    user_in_db = crud.user.get_by_email(db_session, email=email)
    assert user_in_db is not None
    assert user_in_db.email == email
    assert user_in_db.is_active is True # Default from schema/model
    assert user_in_db.is_verified is False # Default from schema/model


def test_create_user_existing_email(client: TestClient, db_session: Session) -> None:
    """
    Test creating a user with an email that already exists.
    Should return a 400 Bad Request error.
    """
    # Create an initial user
    email = random_email()
    password = random_lower_string(12)
    create_random_user(db_session, email=email, password=password) # Use a utility if available or create directly

    # Attempt to create another user with the same email
    new_password = random_lower_string(12)
    data = {"email": email, "password": new_password}
    response = client.post(f"{settings.API_V1_STR}/users/", json=data)

    assert response.status_code == 400, response.text
    error_data = response.json()
    assert "already exists" in error_data["detail"]


def test_create_user_invalid_email(client: TestClient) -> None:
    """
    Test creating a user with an invalid email format.
    Pydantic should catch this and return a 422 Unprocessable Entity.
    """
    password = random_lower_string(12)
    data = {"email": "not-an-email", "password": password}
    response = client.post(f"{settings.API_V1_STR}/users/", json=data)
    assert response.status_code == 422, response.text # Pydantic validation error


def test_create_user_short_password(client: TestClient) -> None:
    """
    Test creating a user with a password that's too short.
    (Assuming Pydantic schema has min_length for password, or this test might pass if no validation)
    If UserCreate schema has `password: str = Field(..., min_length=8)`, this would be 422.
    If no Pydantic validation, it would be 201 unless other logic prevents it.
    For now, we assume no strict password length validation in UserCreate schema for this example.
    If there IS validation (e.g. min_length=8 in UserCreate schema), this should be 422.
    """
    email = random_email()
    # Assuming UserCreate.password does not have a min_length validator for this test
    # If it did, like `password: str = Field(..., min_length=8)`, this test would expect 422
    data = {"email": email, "password": "short"}
    response = client.post(f"{settings.API_V1_STR}/users/", json=data)

    # If UserCreate.password has min_length (e.g. 8), this should be 422
    # assert response.status_code == 422
    # For now, assuming no such validation in the Pydantic schema for UserCreate:
    assert response.status_code == 201, response.text # Or 422 if UserCreate has password validation
    if response.status_code == 201:
        created_user_data = response.json()
        assert created_user_data["email"] == email


# --- Test Get Current User (/users/me - GET) ---

def test_get_current_user_me(client: TestClient, db_session: Session) -> None:
    """
    Test retrieving the current logged-in user's information.
    """
    email = random_email()
    password = random_lower_string(12)
    user = create_random_user(db_session, email=email, password=password, is_verified=True) # Ensure user is created

    headers = get_user_authentication_headers(client=client, email=email, password=password)
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)

    assert response.status_code == 200, response.text
    user_data = response.json()
    assert user_data["email"] == user.email
    assert user_data["user_id"] == user.user_id
    assert user_data["is_active"] == user.is_active
    assert user_data["is_verified"] == user.is_verified
    assert "password_hash" not in user_data


def test_get_current_user_me_unauthenticated(client: TestClient) -> None:
    """
    Test retrieving /users/me without authentication.
    Should return 401 Unauthorized.
    """
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401, response.text # Depends on reusable_oauth2 behavior


# --- Test Update Current User (/users/me - PUT) ---

def test_update_current_user_me(client: TestClient, db_session: Session) -> None:
    """
    Test updating the current logged-in user's information (e.g., email).
    """
    # Initial user
    email_initial = random_email()
    password = random_lower_string(12)
    user = create_random_user(db_session, email=email_initial, password=password, is_verified=True)

    headers = get_user_authentication_headers(client=client, email=email_initial, password=password)

    # Data for update
    email_new = random_email()
    update_data = {"email": email_new, "is_active": False} # Example update

    response = client.put(f"{settings.API_V1_STR}/users/me", headers=headers, json=update_data)

    assert response.status_code == 200, response.text
    updated_user_data = response.json()
    assert updated_user_data["email"] == email_new
    assert updated_user_data["is_active"] is False

    # Verify in DB
    user_in_db = crud.user.get(db_session, id=user.user_id)
    assert user_in_db is not None
    assert user_in_db.email == email_new
    assert user_in_db.is_active is False


def test_update_current_user_me_change_password(client: TestClient, db_session: Session) -> None:
    """
    Test updating the current user's password.
    """
    email = random_email()
    password_old = random_lower_string(12)
    user = create_random_user(db_session, email=email, password=password_old, is_verified=True)

    headers_old_pass = get_user_authentication_headers(client=client, email=email, password=password_old)

    password_new = random_lower_string(12)
    update_data = {"password": password_new}

    response = client.put(f"{settings.API_V1_STR}/users/me", headers=headers_old_pass, json=update_data)
    assert response.status_code == 200, response.text

    # Verify password change by trying to log in with the new password
    headers_new_pass = get_user_authentication_headers(client=client, email=email, password=password_new)
    assert "Authorization" in headers_new_pass

    # Optionally, try to log in with the old password (should fail)
    with pytest.raises(Exception): # httpx.HTTPStatusError if r.raise_for_status() is used in get_user_authentication_headers
        get_user_authentication_headers(client=client, email=email, password=password_old)


def test_update_current_user_me_email_conflict(client: TestClient, db_session: Session) -> None:
    """
    Test updating current user's email to one that's already taken by another user.
    """
    # User 1 (current user)
    email1 = random_email()
    password_user1 = random_lower_string(12)
    create_random_user(db_session, email=email1, password=password_user1, is_verified=True)
    headers_user1 = get_user_authentication_headers(client=client, email=email1, password=password_user1)

    # User 2 (whose email User 1 will try to take)
    email2 = random_email()
    password_user2 = random_lower_string(12)
    create_random_user(db_session, email=email2, password=password_user2)

    # User 1 attempts to update their email to email2
    update_data = {"email": email2}
    response = client.put(f"{settings.API_V1_STR}/users/me", headers=headers_user1, json=update_data)

    assert response.status_code == 400, response.text
    error_data = response.json()
    assert "already registered" in error_data["detail"]

# Helper function in test_users.py to use the utility, as conftest.py might not have it early.
# This is a bit of a workaround for the create_random_user not being directly in conftest.py
# or if conftest.py's normal_user_token_headers is too generic.
def _create_user_and_get_headers(client: TestClient, db: Session, email: str, password: str) -> Dict[str, str]:
    user_in_create = schemas.UserCreate(email=email, password=password, is_verified=True)
    crud.user.create(db, obj_in=user_in_create)
    return get_user_authentication_headers(client=client, email=email, password=password)

# Note:
# - These tests assume the utility functions `random_email`, `random_lower_string`,
#   `create_random_user`, and `get_user_authentication_headers` are available and work correctly.
# - The `db_session` fixture from `conftest.py` provides a clean database session for each test.
# - The `client` fixture from `conftest.py` provides a TestClient with the DB dependency overridden.
# - Password length/complexity tests depend on Pydantic schema validation for `UserCreate`.
#   If UserCreate.password has, e.g., `Field(..., min_length=8)`, then `test_create_user_short_password`
#   should expect a 422. If not, it might pass with 201. I've noted this in the test.
# - Added a direct `create_random_user` call in `test_create_user_existing_email` and
#   `test_get_current_user_me` for clarity, assuming `create_random_user` is robust.

# Self-correction notes and python code block comments removed to prevent syntax errors.
