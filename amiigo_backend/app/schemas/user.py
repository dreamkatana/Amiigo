from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

# --- Base Schemas ---
# These contain common fields shared across other schemas.

class UserBase(BaseModel):
    """
    Base Pydantic schema for User.
    Contains fields that are common for creating and reading users.
    """
    email: EmailStr # Ensures the email format is valid
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    # Add other fields that are common and always present or optional but shareable
    # e.g., first_name, last_name if they were directly on the User model and not Profile

    # Pydantic V2 model configuration
    model_config = ConfigDict(
        from_attributes=True,  # Allows Pydantic to read data from ORM model attributes
        extra='ignore'         # Ignore extra fields not defined in the schema
    )

# --- Schemas for Creation ---

class UserCreate(UserBase):
    """
    Pydantic schema for creating a new User.
    Inherits from UserBase and adds password.
    """
    password: str # Plain password, will be hashed before saving

# --- Schemas for Updating ---

class UserUpdate(UserBase):
    """
    Pydantic schema for updating an existing User.
    All fields are optional.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = None # For password change functionality
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    # Add other updatable fields here

# --- Schemas for Database Representation (Internal) ---

class UserInDBBase(UserBase):
    """
    Base schema for User data as stored in the database.
    Includes fields that are present in the DB model.
    """
    user_id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None

    # Pydantic V2 model configuration (already inherited from UserBase if it has it, but good to be explicit)
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserInDBBase):
    """
    Pydantic schema representing a User object directly from the database.
    This might include the hashed password if needed internally, but typically
    it's excluded from schemas returned to the client.
    """
    password_hash: str # Hashed password

# --- Schemas for API Responses (Public) ---

class User(UserInDBBase):
    """
    Pydantic schema for representing a User in API responses.
    This schema should NOT include sensitive information like password_hash.
    Inherits fields like user_id, email, created_at, etc., from UserInDBBase.
    """
    # Profile information might be nested here if desired for some endpoints
    # profile: Optional[Profile] = None # Assuming a Profile schema exists

    # Example: if you want to add a full name computed from a profile
    # full_name: Optional[str] = None

    pass # Inherits all necessary fields from UserInDBBase for public display


# Example of a schema for user registration response (could be same as User schema)
class UserRegistered(User):
    """
    Schema for the response after a user is successfully registered.
    Often similar to the main User schema for public display.
    """
    pass


# If you need a very minimal user representation for some contexts:
class UserSimple(BaseModel):
    user_id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

# ``` # Removed offending backticks
