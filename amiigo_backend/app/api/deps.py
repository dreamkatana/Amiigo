from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from jose import jwt, JWTError # JWTError might be needed if decode_access_token raises it specifically
# from pydantic import ValidationError # Not directly needed here for token decoding path
from sqlalchemy.orm import Session

from app.core import security # Access security functions (token decoding)
from app.core.config import settings # Access settings (secret key, algorithm)
from app.db.session import SessionLocal # To create DB sessions
from app.models.user import User # User model for fetching user from DB
from app.crud.crud_user import user as crud_user # CRUD operations for user
# from app.schemas.token import TokenPayload # Not strictly needed here if decode_access_token returns subject directly

# OAuth2PasswordBearer scheme for token authentication in Swagger UI / ReDoc
# tokenUrl should point to your login endpoint that issues tokens.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    Ensures the session is closed after the request is finished.
    """
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    FastAPI dependency to get the current authenticated user from a JWT token.

    Validates the token, decodes it, retrieves the user from the database.

    :param db: SQLAlchemy database session from `get_db` dependency.
    :param token: JWT token from the `Authorization: Bearer <token>` header.
    :return: The authenticated User model instance.
    :raises HTTPException:
        - 401 Unauthorized: If token is invalid, user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    subject_from_token = security.decode_access_token(token)
    if subject_from_token is None: # Token invalid, expired, or 'sub' claim missing/empty
        raise credentials_exception

    try:
        # Assuming 'sub' from the token (subject_from_token) contains the user_id as a string.
        user_id = int(subject_from_token)
    except ValueError:
        # If 'sub' is not a valid integer string for user_id
        # This indicates a malformed token or incorrect 'sub' claim format.
        raise credentials_exception

    db_user = crud_user.get(db, id=user_id)
    if db_user is None:
        # User ID from token does not correspond to any user in the database.
        raise credentials_exception

    return db_user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency to get the current authenticated and *active* user.
    Relies on `get_current_user` to first authenticate and retrieve the user.

    :param current_user: User model instance from `get_current_user` dependency.
    :return: The active authenticated User model instance.
    :raises HTTPException:
        - 403 Forbidden: If the user is inactive.
    """
    if not crud_user.is_active(current_user): # Assumes User model has `is_active` attribute
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


def get_current_active_verified_user(
    current_user: User = Depends(get_current_active_user), # Chain dependencies
) -> User:
    """
    FastAPI dependency to get the current authenticated, active, and *verified* user.
    Relies on `get_current_active_user`.

    :param current_user: User model instance from `get_current_active_user` dependency.
    :return: The active, verified, authenticated User model instance.
    :raises HTTPException:
        - 403 Forbidden: If the user is not verified.
    """
    if not crud_user.is_verified(current_user): # Assumes User model has `is_verified` attribute
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has not verified their email address."
        )
    return current_user


# Example for a superuser/admin check (if you add `is_superuser` to your User model/CRUD):
# def get_current_active_superuser(
#     current_user: User = Depends(get_current_active_user),
# ) -> User:
#     if not crud_user.is_superuser(current_user): # Assumes is_superuser method/attribute exists
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="The user doesn't have enough privileges"
#         )
#     return current_user
# ``` # Removed offending backticks
