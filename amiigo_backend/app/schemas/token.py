from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    """
    Pydantic schema for the JWT access token response.
    """
    access_token: str
    token_type: str = "bearer" # Typically "bearer"

class TokenPayload(BaseModel):
    """
    Pydantic schema for the data encoded within the JWT access token.
    This represents the "claims" of the token.
    """
    sub: Optional[str] = None # Subject of the token (e.g., user_id or email)
    exp: Optional[int] = None # Expiry time (timestamp)

class TokenData(BaseModel):
    """
    Pydantic schema for holding the data extracted from the token's payload,
    typically the user identifier (e.g., email or user_id).
    Used after decoding the token.
    """
    # Using user_id as an example, adjust if email or other identifier is stored in 'sub'
    user_id: Optional[int] = None
    # Or, if you store email in the 'sub' claim:
    # email: Optional[EmailStr] = None


# Schema for requesting a new token (e.g., login)
# This is often handled by FastAPI's OAuth2PasswordRequestForm,
# but if you want a JSON body for login, you'd define a schema like this:
class TokenRequest(BaseModel):
    """
    Pydantic schema for requesting a token via username/password (JSON body).
    """
    username: EmailStr # Assuming email is used as username
    password: str
# ``` # Removed offending backticks
