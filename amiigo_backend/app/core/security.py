from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import settings

# Password Hashing Context
# Using bcrypt as the default hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    :param plain_password: The password in plain text.
    :param hashed_password: The hashed password stored in the database.
    :return: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain password.

    :param password: The password in plain text.
    :return: The hashed password.
    """
    return pwd_context.hash(password)

def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    :param subject: The subject of the token (e.g., user_id or email).
    :param expires_delta: Optional timedelta for token expiry. If None, uses default from settings.
    :return: The encoded JWT access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    """
    Decodes a JWT access token.

    :param token: The JWT token to decode.
    :return: The subject (e.g., user_id) if the token is valid and not expired, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: Optional[str] = payload.get("sub")
        if subject is None:
            return None # Or raise an exception
        return subject
    except JWTError: # Catches various errors like expired token, invalid signature, etc.
        return None # Or raise a specific exception

# Example usage (can be removed or used in tests)
# if __name__ == "__main__":
#     # Password Hashing Example
#     plain_pass = "mysecretpassword"
#     hashed_pass = get_password_hash(plain_pass)
#     print(f"Plain password: {plain_pass}")
#     print(f"Hashed password: {hashed_pass}")
#     print(f"Verification successful: {verify_password(plain_pass, hashed_pass)}")
#     print(f"Verification failure (wrong pass): {verify_password('wrongpassword', hashed_pass)}")

#     # JWT Token Example
#     user_identifier = "user123"
#     access_token = create_access_token(subject=user_identifier)
#     print(f"\nAccess token for '{user_identifier}': {access_token}")

#     decoded_subject = decode_access_token(access_token)
#     if decoded_subject:
#         print(f"Decoded subject from token: {decoded_subject}")
#     else:
#         print("Failed to decode token or token is invalid/expired.")

    # Example of an expired token
    # short_lived_token = create_access_token(subject="test_expiry", expires_delta=timedelta(seconds=1))
    # import time
    # time.sleep(2) # Wait for the token to expire
    # print(f"\nAttempting to decode expired token: {decode_access_token(short_lived_token)}")
# ``` # Removed offending backticks
