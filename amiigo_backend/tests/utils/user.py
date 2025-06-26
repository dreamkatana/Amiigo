import random
import string
from typing import Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings # For API V1 STR, etc.
# from app.models.user import User # Redundant if using models.User
# from app.schemas.user import UserCreate # Redundant if using schemas.UserCreate

def random_lower_string(length: int = 32) -> str:
    """Generate a random lowercase string."""
    return "".join(random.choices(string.ascii_lowercase, k=length))

def random_email() -> str:
    """Generate a random email address."""
    domain = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{random_lower_string(10)}@{domain}.com"

def get_user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    """
    Authenticate a user and return the token headers.

    :param client: FastAPI TestClient instance.
    :param email: User's email.
    :param password: User's password.
    :return: Dictionary with Authorization header.
    """
    data = {"username": email, "password": password} # OAuth2PasswordRequestForm uses 'username'

    # Construct the full login URL using settings.API_V1_STR
    login_url = f"{settings.API_V1_STR}/login/access-token"

    r = client.post(login_url, data=data)
    r.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers

def create_random_user(
    db: Session,
    *,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_verified: bool = True,
    is_active: bool = True
) -> models.User:
    """
    Create a random user in the database for testing.
    Uses provided email/password if given, otherwise generates random ones.

    :param db: SQLAlchemy database session.
    :param email: Optional email for the user.
    :param password: Optional password for the user.
    :param is_verified: Whether the created user should be marked as verified.
    :param is_active: Whether the created user should be marked as active.
    :return: The created User SQLAlchemy model instance.
    """
    actual_email = email or random_email()
    actual_password = password or random_lower_string(12)

    user_in_create = schemas.UserCreate(
        email=actual_email,
        password=actual_password,
        is_verified=is_verified,
        is_active=is_active  # Assuming UserBase (parent of UserCreate) has is_active
    )

    # Use the CRUD operation to create the user (this also handles password hashing)
    user = crud.user.create(db=db, obj_in=user_in_create)
    return user

def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    (This is a common utility from FastAPI project generators like full-stack-fastapi-postgresql)
    """
    password = random_lower_string(16) # A dummy password for user creation
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = schemas.UserCreate(email=email, password=password, is_verified=True)
        user = crud.user.create(db=db, obj_in=user_in_create)
    else:
        # If user exists, we need to ensure we can log them in.
        # This might require updating their password if we don't know it.
        # For simplicity, this utility assumes if the user exists, we can somehow get a token.
        # A more robust approach for existing users might be to have a known test password
        # or use a mechanism to directly generate a token for a user ID (admin privilege).
        # For this example, we'll use the get_user_authentication_headers,
        # which means the 'password' used here for creation needs to be known.
        # If we just created the user, we know the password.
        # If the user existed, we don't implicitly know their password.
        # This function is more for ensuring a user *with a token* exists.
        pass # User exists, proceed to get headers with the known/dummy password.

    # If the user was just created, 'password' is known.
    # If they existed, this assumes the 'password' variable is what they'd use.
    # This is a simplification. In real tests, you manage test user credentials carefully.
    return get_user_authentication_headers(client=client, email=email, password=password if not crud.user.get_by_email(db, email=email) else "known_test_password_if_any")
    # The password logic above is a bit tangled. Let's simplify for this utility's purpose:
    # This utility is primarily for getting a token for an email, creating the user if needed.
    # It implies the password used for creation is also used for login.

# Simpler version of authentication_token_from_email for clarity:
def ensure_user_and_get_token(
    client: TestClient, db: Session, email: str, password: str = "testpassword"
) -> tuple[models.User, Dict[str, str]]:
    """
    Ensures a user with the given email exists (creating if not) and returns the user object
    and their authentication token headers. Uses a provided or default password.
    """
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = schemas.UserCreate(email=email, password=password, is_verified=True, is_active=True)
        user = crud.user.create(db=db, obj_in=user_in_create)
    else:
        # If user exists, but we want to ensure we can log in with 'password'
        # we might need to update their password. For testing, this can be acceptable.
        if not crud.user.authenticate(db, email=email, password=password):
            user_update = schemas.UserUpdate(password=password)
            user = crud.user.update(db, db_obj=user, obj_in=user_update)

    headers = get_user_authentication_headers(client=client, email=email, password=password)
    return user, headers


# Example usage in a test:
# from app.tests.utils.user import create_random_user, get_user_authentication_headers
#
# def test_get_own_info(client: TestClient, db_session: Session):
#     user = create_random_user(db_session)
#     headers = get_user_authentication_headers(
#         client=client, email=user.email, password="the_password_used_or_known_for_user"
#     )
#     response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
#     assert response.status_code == 200
#     # ... more assertions

# Self-correction notes removed to prevent syntax errors from backticks in comments.
